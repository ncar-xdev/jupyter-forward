import datetime
import os

import pytest

import jupyter_forward

NOT_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') is None
requires_gha = pytest.mark.skipif(NOT_GITHUB_ACTIONS, reason='requires GITHUB_ACTIONS')


@pytest.fixture(scope='session', params=[f"{os.environ['USER']}@eniac.local"])
def runner(request):
    remote = jupyter_forward.RemoteRunner(request.param)
    yield remote
    remote.close()


@requires_gha
def test_connection(runner):
    USER = os.environ['USER']
    assert runner.session.is_connected
    assert runner.session.host == '127.0.0.1'
    assert runner.session.user == USER


@requires_gha
@pytest.mark.parametrize('command', ['echo $HOME'])
def test_run_command(runner, command):
    out = runner.run_command(command)
    assert not out.failed
    assert out.stdout.strip() == f"{os.environ['HOME']}"


@requires_gha
@pytest.mark.parametrize('command', ['echod $HOME'])
def test_run_command_failure(runner, command):
    out = runner.run_command(command, exit=False)
    assert out.failed
    assert 'echod: command not found' in out.stdout.strip()

    with pytest.raises(SystemExit):
        runner.run_command(command)


@requires_gha
def test_set_logs(runner):
    runner._set_log_directory()
    assert runner.log_dir == f"{os.environ['HOME']}/.jupyter_forward"
    runner._set_log_file()
    now = datetime.datetime.now()
    assert f"log_{now.strftime('%Y-%m-%dT%H')}" in runner.log_file
