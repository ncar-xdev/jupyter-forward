import datetime
import os

import pytest

import jupyter_forward

SHELLS = ['bash', 'sh', 'tcsh', 'zsh', None]
NOT_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') is None
requires_gha = pytest.mark.skipif(NOT_GITHUB_ACTIONS, reason='requires GITHUB_ACTIONS')


@pytest.fixture(scope='session')
def runner(request):
    remote = jupyter_forward.RemoteRunner(f"{os.environ['USER']}@eniac.local", shell=request.param)
    yield remote
    remote.close()


@requires_gha
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_connection(runner):
    USER = os.environ['USER']
    assert runner.session.is_connected
    assert runner.session.host == '127.0.0.1'
    assert runner.session.user == USER


@requires_gha
@pytest.mark.parametrize('command', ['echo $HOME'])
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_run_command(runner, command):
    out = runner.run_command(command)
    assert not out.failed
    f"{os.environ['HOME']}" in out.stdout.strip()


@requires_gha
@pytest.mark.parametrize('command', ['echod $HOME'])
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_run_command_failure(runner, command):
    out = runner.run_command(command, exit=False)
    assert out.failed
    assert 'not found' in out.stdout.strip().lower()

    with pytest.raises(SystemExit):
        runner.run_command(command)


@requires_gha
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_set_logs(runner):
    runner._set_log_directory()
    assert '/.jupyter_forward' in runner.log_dir
    runner._set_log_file()
    now = datetime.datetime.now()
    assert f"log_{now.strftime('%Y-%m-%dT%H')}" in runner.log_file


@requires_gha
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_prepare_batch_job_script(runner):
    runner._set_log_directory()
    script_file = runner._prepare_batch_job_script("echo 'hello world'")
    assert 'batch_job_script' in script_file
    assert "echo 'hello world'" in runner.run_command(f'cat {script_file}').stdout.strip()


@requires_gha
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_parse_log_file(runner, sample_log_file):
    runner._set_log_directory()
    runner.log_file = sample_log_file
    out = runner._parse_log_file()
    assert out == {
        'hostname': 'eniac01',
        'port': '59628',
        'token': 'Loremipsumdolorsitamet',
        'url': 'http://eniac01:59628/?token=Loremipsumdolorsitamet',
    }


@pytest.mark.skip(reason='Unable to diagnose CI issue causing this to fail')
@requires_gha
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
@pytest.mark.parametrize('environment', ['jupyter-forward-dev', None])
def test_conda_activate_cmd(runner, environment):
    runner.conda_env = environment
    cmd = runner._conda_activate_cmd()
    assert cmd in ['source activate', 'conda activate']


@requires_gha
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_conda_activate_cmd_error(runner):
    runner.conda_env = 'DOES_NOT_EXIST'
    with pytest.raises(SystemExit):
        runner._conda_activate_cmd()


@requires_gha
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_generate_redirect_cmd(runner):
    runner._set_log_directory()
    runner._set_log_file()
    cmd = runner._generate_redirect_command(command='echo "hello world"', log_file=runner.log_file)
    if 'csh' in runner.shell:
        assert cmd.endswith(runner.log_file)
    else:
        assert cmd.endswith(f'{runner.log_file} 2>&1')
