import os

import pytest
from typer.testing import CliRunner

from jupyter_forward.core import app

GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS', False)
print(GITHUB_ACTIONS)
runner = CliRunner()


def test_help():
    result = runner.invoke(app, ['--help'])
    assert 'Jupyter Lab Port Forwarding Utility' in result.stdout
    assert 'Starts Jupyter lab' in result.stdout
    assert 'Prints an ssh configuration' in result.stdout


def test_config():
    result = runner.invoke(app, ['config', 'cheyenne', 'mariecurie'])
    assert 'Host cheyenne' in result.stdout
    assert 'User mariecurie' in result.stdout


@pytest.mark.skipif(not GITHUB_ACTIONS, reason='Needs to run as part of the GitHub action workflow')
def test_start():
    _ = runner.invoke(app, ['start', 'root@localhost'])
