import typer.testing

from jupyter_forward.cli import app

runner = typer.testing.CliRunner()


def test_help():
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0
    assert 'show this message and exit'.lower() in result.stdout.lower()


def test_version():
    result = runner.invoke(app, ['--version'])
    assert result.exit_code == 0
    assert 'Jupyter Forward CLI Version'.lower() in result.stdout.lower()
