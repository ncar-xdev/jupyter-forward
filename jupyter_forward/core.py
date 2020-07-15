import dataclasses
import getpass
import random
from collections import namedtuple

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
):
    """
    Starts Jupyter lab on a remote resource and port forwards session to
    local machine.
    """
    password = getpass.getpass()
    session = Connection(host, connect_kwargs={'password': password})
    command = f'conda activate {conda_env} &&  jupyter lab --no-browser --ip=`hostname` --port={port} --notebook-dir={notebook_dir}'
    return session.run(command, asynchronous=True)


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
