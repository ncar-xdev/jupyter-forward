import datetime
import os

import pytest

import jupyter_forward

NOT_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') is None
requires_gha = pytest.mark.skipif(NOT_GITHUB_ACTIONS, reason='requires GITHUB_ACTIONS')


@pytest.fixture(scope='session')
def runner(request):
    remote = jupyter_forward.RemoteRunner(f"{os.environ['USER']}@eniac.local", shell=request.param)
    yield remote
    remote.close()


@requires_gha
@pytest.mark.parametrize('runner', ['bash', 'sh', 'tcsh', 'zsh'], indirect=True)
def test_connection(runner):
    USER = os.environ['USER']
    assert runner.session.is_connected
    assert runner.session.host == '127.0.0.1'
    assert runner.session.user == USER


@requires_gha
@pytest.mark.parametrize('command', ['echo $HOME'])
@pytest.mark.parametrize('runner', ['bash', 'sh', 'tcsh', 'zsh'], indirect=True)
def test_run_command(runner, command):
    out = runner.run_command(command)
    assert not out.failed
    assert out.stdout.strip() == f"{os.environ['HOME']}"


@requires_gha
@pytest.mark.parametrize('command', ['echod $HOME'])
@pytest.mark.parametrize('runner', ['bash', 'sh', 'tcsh', 'zsh'], indirect=True)
def test_run_command_failure(runner, command):
    out = runner.run_command(command, exit=False)
    assert out.failed
    assert 'not found' in out.stdout.strip().lower()

    with pytest.raises(SystemExit):
        runner.run_command(command)


@requires_gha
@pytest.mark.parametrize('runner', ['bash', 'sh', 'tcsh', 'zsh'], indirect=True)
def test_set_logs(runner):
    runner._set_log_directory()
    assert '/.jupyter_forward' in runner.log_dir
    runner._set_log_file()
    now = datetime.datetime.now()
    assert f"log_{now.strftime('%Y-%m-%dT%H')}" in runner.log_file
