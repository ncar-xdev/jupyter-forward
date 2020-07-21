import dataclasses
import getpass
import random
import time
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


def open_browser(port: int = None, token: str = None, url: str = None):
    """
    Opens notebook interface in a new browser window.

    Parameters
    ----------
    port : int, optional
        Port number to use, by default None
    token : str, optional
        token used for authentication, by default None
    url : str, optional
        Notebook url, by default None

    Raises
    ------
    ValueError
        If url is None and port is None
    """

    import webbrowser

    if not url:
        if port is None:
            raise ValueError('Please specify port number to use.')
        url = f'http://localhost:{port}'
        if token:
            url = f'{url}/?token={token}'
    print(f'*** Opening Jupyter Lab interface in a browser at ***\n*** {url} ***')
    webbrowser.open(url, new=2)


def setup_port_forwarding(port: int, username: str, hostname: str, host: str):
    """
    Sets up SSH port forwarding

    Parameters
    ----------
    port : int
        port number to use
    username : str
    hostname : str
    host     : str
    """
    print('*** Setting up port forwarding ***')
    command = f'ssh -N -L localhost:{port}:{hostname}:{port} {username}@{host}'
    print(command)
    invoke.run(command, asynchronous=True)
    time.sleep(3)


def parse_stdout(stdout: str):
    """
    Parses stdout to determine remote_hostname, port, token, url

    Parameters
    ----------
    stdout : str
        Contents of the log file/stdout

    Returns
    -------
    dict
        A dictionary containing hotname, port, token, and url
    """
    import re
    import urllib.parse

    hostname, port, token, url = None, None, None, None
    urls = set(
        re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            stdout,
        )
    )
    for url in urls:
        url = url.strip()
        if '127.0.0.1' not in url:
            result = urllib.parse.urlparse(url)
            hostname, port = result.netloc.split(':')
            if 'token' in result.query:
                token = result.query.split('token=')[-1].strip()
            break
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

    # jupyter lab will pipe output to logfile, which should not exist prior to running
    # Logfile will be in $TMPDIR if defined on the remote machine, otherwise in $HOME
    tmpdir = session.run('echo $TMPDIR', hide='out').stdout.strip()
    if len(tmpdir) == 0:
        tmpdir = session.run('echo $HOME', hide='out').stdout.strip()
        if len(tmpdir) == 0:
            tmpdir = '~'
    log_dir = f'{tmpdir}/.jupyter_forward'
    session.run(f'mkdir -p {log_dir}', hide='out')
    logfile = f'{log_dir}/jforward.{port}'
    session.run(f'rm -f {logfile}', hide='out')

    # start jupyter lab on remote machine
    command = f'conda activate {conda_env} &&  jupyter lab --no-browser --ip=`hostname` --port={port} --notebook-dir={notebook_dir}'
    _ = session.run(f'{command} > {logfile} 2>&1', asynchronous=True)
    # wait for logfile to contain access info, then write it to screen
    condition = True
    stdout = None
    pattern = 'The Jupyter Notebook is running at:'
    while condition:
        try:
            result = session.run(f'tail {logfile}', hide='out')
            if pattern in result.stdout:
                condition = False
                stdout = result.stdout
        except invoke.exceptions.UnexpectedExit:
            print(f'Trying to access {logfile} on {host} again...')
            pass

    parsed_result = parse_stdout(stdout)
    print(parsed_result)
    if port_forwarding:
        setup_port_forwarding(
            parsed_result['port'], session.user, parsed_result['hostname'], session.host
        )
        open_browser(port=parsed_result['port'], token=parsed_result['token'])
    else:
        open_browser(url=parsed_result['url'])

    session.run(f'tail -f {logfile}')


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
