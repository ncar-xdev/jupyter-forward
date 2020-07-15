import dataclasses
import random
from collections import namedtuple
from typing import NamedTuple

import typer

app = typer.Typer()


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
def start():
    """
    Jupyter lab/notebook Port Forwarding Utility
    """
    pass


def main():
    typer.run(app())
