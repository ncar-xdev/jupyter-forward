import dataclasses
import getpass
import random
import time
import urllib.parse
from collections import namedtuple

import invoke
import typer
from fabric import Connection

random.seed(42)


app = typer.Typer(help='Jupyter Lab Port Forwarding Utility')


@dataclasses.dataclass
class Config:
    host: str
    hostname: str
    username: str

    def run(self):
        template = f"""
Host {self.host}
    User {self.username}
    Hostname {self.hostname}
    GSSAPIDelegateCredentials yes
    GSSAPIAuthentication yes
    ControlMaster auto
    ControlPersist yes
    ControlPath ~/.ssh/control/%C
        """
        print(template)


def open_browser(port=None, token=None, url=None):
    import webbrowser

    if not url:
        if port is None:
            raise ValueError('Please specify port number to use.')
        url = f'http://localhost:{port}'
        if token:
            url = f'{url}/?token={token}'
    print(f'*** Opening Jupyter Lab interface in a browser at ***\n*** {url} ***')
    webbrowser.open(url, new=2)


def setup_port_forwarding(port, username, hostname):
    print('*** Setting up port forwarding ***')
    command = f'ssh -N -L {port}:localhost:{port} {username}@{hostname}'
    print(command)
    invoke.run(command, asynchronous=True)
    time.sleep(3)


def parse_stdout(stdout):
    hostname, port, token, url = None, None, None, None
    stdout = stdout.splitlines()
    for line in stdout:
        line = line.strip()
        if line.startswith('http') and ('127.0.0.1' not in line):
            result = urllib.parse.urlparse(line)
            url = line
            hostname, port = result.netloc.split(':')
            if 'token' in result.query:
                token = result.query.split('token=')[-1].strip()
    return {'hostname': hostname, 'port': port, 'token': token, 'url': url}


@app.command()
def config(host: str, username: str, hostname: str = typer.Option(None, show_default=True)):
    """
    Prints an ssh configuration for the user, selecting a
    login node at random if host has multiple login nodes.
    """

    Machine = namedtuple('Machine', ['domain', 'login_node'])

    machines = {
        'cheyenne': Machine('ucar.edu', random.choice(range(1, 7))),
        'casper': Machine('ucar.edu', random.choice((6, 26))),
        'hobart': Machine('cgd.ucar.edu', None),
    }

    if not hostname:
        try:
            m = machines[host]
            if m.login_node:
                hostname = f'{host}{m.login_node}.{m.domain}'
            else:
                hostname = f'{host}.{m.domain}'
        except KeyError:
            raise ValueError(
                f'Unable to find hostname information for `{host}` in the list of registered hosts: {list(machines.keys())}. Specify hostname via --hostname option.'
            )

    config = Config(host, hostname, username)
    config.run()


@app.command()
def start(
    host: str,
    port: int = typer.Option(
        random.choice(range(49152, 65335)),
        help='The port the notebook server will listen on. If not specified, uses a random port',
        show_default=True,
    ),
    conda_env: str = typer.Option(
        'base', show_default=True, help='Name of conda environment that contains jupyter lab'
    ),
    notebook_dir: str = typer.Option(
        '$HOME', show_default=True, help='The directory to use for notebooks'
    ),
    port_forwarding: bool = typer.Option(
        True, show_default=True, help='Whether to set up SSH port forwarding or not'
    ),
):
    """
    Starts Jupyter lab on a remote resource and port forwards session to
    local machine.
    """
    password = getpass.getpass()
    session = Connection(host, connect_kwargs={'password': password})
    logfile = f'~/.jforward.{port}'
    command = f'conda activate {conda_env} &&  jupyter lab --no-browser --ip=`hostname` --port={port} --notebook-dir={notebook_dir}'
    jlab_exe = session.run(f'{command} > {logfile} 2>&1', asynchronous=True)
    print(f'DEBUG: jlab_exe is of type {type(jlab_exe)}')
    condition = True
    pattern = 'To access the notebook, open this file in a browser:'
    stdout = None
    while condition:
        result = session.run(f'tail {logfile}', hide='out')
        if pattern in result.stdout:
            condition = False
            stdout = result.stdout

    parsed_result = parse_stdout(stdout)
    if port_forwarding:
        setup_port_forwarding(parsed_result['port'], session.user, parsed_result['hostname'])
        open_browser(port=parsed_result['port'], token=parsed_result['token'])
    open_browser(url=parsed_result['url'])


@app.command()
def resume():
    """
    Resumes an already running remote Jupyter Lab session.
    """
    ...


@app.command()
def end():
    """
    Stops the running Jupyter Lab server.
    """
    ...


def main():
    typer.run(app())
