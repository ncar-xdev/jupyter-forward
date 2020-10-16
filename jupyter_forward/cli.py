import typer

from .core import JupyterLabRunner

app = typer.Typer(help='Jupyter Lab Port Forwarding Utility')


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
        'base',
        show_default=True,
        help='Name of conda environment on the remote host that contains jupyter lab',
    ),
    notebook_dir: str = typer.Option(
        '$HOME',
        show_default=True,
        help='The directory on the remote host to use for notebooks',
    ),
    port_forwarding: bool = typer.Option(
        True, show_default=True, help='Whether to set up SSH port forwarding or not'
    ),
    identity: str = typer.Option(
        None,
        show_default=True,
        help=(
            '''Selects a file from which the identity (private key) for public key authentication is read.'''
        ),
    ),
):
    """
    Starts Jupyter lab on a remote resource and port forwards session to
    local machine.
    """

    runner = JupyterLabRunner(host, port, conda_env, notebook_dir, port_forwarding, identity)
    runner.start()


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
