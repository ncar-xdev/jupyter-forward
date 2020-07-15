import socket

import pytest
from typer.testing import CliRunner

from jupyter_forward.core import app

runner = CliRunner()


@pytest.fixture()
def ssh():
    sockl = socket.socket()
    sockl.bind(('localhost', 0))
    sockl.listen(1)
    addr, port = sockl.getsockname()
    connect_kwargs = dict(hostname=addr, port=port)
    yield connect_kwargs


def test_help():
    result = runner.invoke(app, ['--help'])
    assert 'Jupyter Lab Port Forwarding Utility' in result.stdout
    assert 'Starts Jupyter lab' in result.stdout
    assert 'Prints an ssh configuration' in result.stdout


def test_config():
    result = runner.invoke(app, ['config', 'cheyenne', 'mariecurie'])
    assert 'Host cheyenne' in result.stdout
    assert 'User mariecurie' in result.stdout
