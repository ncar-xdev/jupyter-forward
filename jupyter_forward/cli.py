from pathlib import Path
from typing import Optional

import typer

from .core import RemoteRunner

app = typer.Typer(help='Jupyter Lab Port Forwarding Utility')


def version_callback(value: bool):
    from pkg_resources import get_distribution

    __version__ = get_distribution('jupyter_forward').version
    if value:
        typer.echo(f'Jupyter Forward CLI Version: {__version__}')
        raise typer.Exit()


@app.command()
def start(
    host: str,
    port: int = typer.Option(
        8888,
        help=(
            '''The local port the remote notebook server will be forwarded to. If not specified, defaults to 8888.'''
        ),
        show_default=True,
    ),
    conda_env: str = typer.Option(
        None,
        show_default=True,
        help='Name of the conda environment on the remote host that contains jupyter lab.',
    ),
    notebook_dir: str = typer.Option(
        None,
        show_default=True,
        help='The directory on the remote host to use for notebooks. Defaults to $HOME.',
    ),
    port_forwarding: bool = typer.Option(
        True, show_default=True, help='Whether to set up SSH port forwarding or not.'
    ),
    identity: Path = typer.Option(
        None,
        '--identity',
        '-i',
        exists=True,
        file_okay=True,
        show_default=True,
        help=(
            '''Selects a file from which the identity (private key) for public key authentication is read.'''
        ),
    ),
    launch_command: str = typer.Option(
        None,
        '--launch-command',
        '-c',
        show_default=True,
        help=(
            '''Custom command to run before launching Jupyter Lab. For instance: "qsub -q regular -l select=1:ncpus=36,walltime=00:05:00 -A AABD1115"'''
        ),
    ),
    shell: str = typer.Option(
        '/usr/bin/sh -l',
        '--shell',
        '-s',
        show_default=True,
        help='Which remote shell binary to use.',
    ),
    version: Optional[bool] = typer.Option(
        None,
        '--version',
        callback=version_callback,
        is_eager=True,
        help=('Display jupyter-forward version'),
    ),
):
    """
    Starts Jupyter lab on a remote resource and port forwards session to
    local machine.
    """

    runner = RemoteRunner(
        host,
        port=port,
        conda_env=conda_env,
        notebook_dir=notebook_dir,
        port_forwarding=port_forwarding,
        launch_command=launch_command,
        identity=identity,
        shell=shell,
    )
    runner.start()


def main():
    typer.run(app())
