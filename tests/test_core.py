import datetime
import json
import os
from contextlib import contextmanager

import pytest

import jupyter_forward

from .misc import sample_log_file_contents

SHELLS = json.loads(os.environ.get('JUPYTER_FORWARD_TEST_SHELLS', '["bash", null]'))
JUPYTER_FORWARD_ENABLE_SSH_TESTS = os.environ.get('JUPYTER_FORWARD_ENABLE_SSH_TESTS') is None
requires_ssh = pytest.mark.skipif(JUPYTER_FORWARD_ENABLE_SSH_TESTS, reason='SSH tests disabled')
ON_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') is not None


@contextmanager
def delete_file(session, path):
    try:
        yield
    finally:
        session.run(f'rm {path}')


@pytest.fixture(scope='package')
def runner(request):
    remote = jupyter_forward.RemoteRunner(
        f"{os.environ['JUPYTER_FORWARD_SSH_TEST_USER']}@{os.environ['JUPYTER_FORWARD_SSH_TEST_HOSTNAME']}",
        shell=request.param,
        auth_handler=lambda t, i, p: ['Loremipsumdolorsitamet'] * len(p),
        fallback_auth_handler=lambda: 'Loremipsumdolorsitamet',
    )
    try:
        yield remote
    finally:
        remote.close()


@requires_ssh
@pytest.mark.parametrize(
    'port, conda_env, notebook, notebook_dir, port_forwarding, identity, shell',
    [
        (8888, None, None, None, True, None, None),
        (8888, None, None, '~/notebooks/', False, None, None),
        (8888, None, '~/my_notebook.ipynb', None, True, None, 'bash'),
        (8888, 'base', None, None, False, None, 'bash'),
    ],
)
def test_runner_init(port, conda_env, notebook, notebook_dir, port_forwarding, identity, shell):
    remote_runner = jupyter_forward.RemoteRunner(
        f"{os.environ['JUPYTER_FORWARD_SSH_TEST_USER']}@{os.environ['JUPYTER_FORWARD_SSH_TEST_HOSTNAME']}",
        port=port,
        conda_env=conda_env,
        notebook=notebook,
        notebook_dir=notebook_dir,
        identity=identity,
        port_forwarding=port_forwarding,
        shell=shell,
        auth_handler=lambda t, i, p: ['Loremipsumdolorsitamet'] * len(p),
        fallback_auth_handler=lambda: 'Loremipsumdolorsitamet',
    )

    assert remote_runner.port == port
    assert remote_runner.conda_env == conda_env


@requires_ssh
def test_runner_init_notebook_dir_error():
    with pytest.raises(ValueError):
        jupyter_forward.RemoteRunner(
            f"{os.environ['JUPYTER_FORWARD_SSH_TEST_USER']}@{os.environ['JUPYTER_FORWARD_SSH_TEST_HOSTNAME']}",
            notebook_dir='~/notebooks/',
            notebook='~/my_notebook.ipynb',
            auth_handler=lambda t, i, p: ['Loremipsumdolorsitamet'] * len(p),
            fallback_auth_handler=lambda: 'Loremipsumdolorsitamet',
        )


@requires_ssh
def test_runner_init_port_unavailable():
    with pytest.raises(SystemExit):
        jupyter_forward.RemoteRunner(
            f"{os.environ['JUPYTER_FORWARD_SSH_TEST_USER']}@{os.environ['JUPYTER_FORWARD_SSH_TEST_HOSTNAME']}",
            port=22,
            auth_handler=lambda t, i, p: ['Loremipsumdolorsitamet'] * len(p),
            fallback_auth_handler=lambda: 'Loremipsumdolorsitamet',
        )


@requires_ssh
def test_runner_authentication_error():
    with pytest.raises(SystemExit):
        jupyter_forward.RemoteRunner(
            f"foobar@{os.environ['JUPYTER_FORWARD_SSH_TEST_HOSTNAME']}",
            auth_handler=lambda t, i, p: ['Loremipsumdolorsitamet'] * len(p),
            fallback_auth_handler=lambda: 'Loremipsumdolorsitamet',
        )


@requires_ssh
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_connection(runner):
    USER = os.environ['JUPYTER_FORWARD_SSH_TEST_USER']
    assert runner.session.is_connected
    assert runner.session.host in [
        '127.0.0.1',
        'localhost',
        {os.environ['JUPYTER_FORWARD_SSH_TEST_HOSTNAME']},
    ]
    assert runner.session.user == USER


@requires_ssh
@pytest.mark.parametrize('command', ['echo $HOME'])
@pytest.mark.parametrize('kwargs', [{}, dict(asynchronous=True)])
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_run_command(runner, command, kwargs):
    out = runner.run_command(command, **kwargs)
    if kwargs.get('asynchronous', False):
        out = out.join()
    assert not out.failed
    f"{os.environ['HOME']}" in out.stdout.strip()


@requires_ssh
@pytest.mark.parametrize('command', ['echod $HOME'])
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_run_command_failure(runner, command):
    out = runner.run_command(command, exit=False)
    assert out.failed
    assert 'not found' in out.stdout.strip().lower()

    with pytest.raises(SystemExit):
        runner.run_command(command)


@requires_ssh
@pytest.mark.parametrize('content', ['echo $HOME', 'echo $(hostname -f)'])
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_put_file(runner, content):
    runner._set_log_directory()
    path = f'{runner.log_dir}/test_file'
    with delete_file(runner.session, path):
        runner.put_file(path, content)

        out = runner.run_command(f'cat {path}')
        assert content == out.stdout


@requires_ssh
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_set_logs(runner):
    runner._set_log_directory()
    assert '/.jupyter_forward' in runner.log_dir
    runner._set_log_file()
    now = datetime.datetime.now()
    assert f"log_{now.strftime('%Y-%m-%dT%H')}" in runner.log_file


@requires_ssh
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_prepare_batch_job_script(runner):
    if ON_GITHUB_ACTIONS and ('csh' in runner.shell):
        pytest.xfail('Fails on GitHub Actions due to inconsistent shell behavior')
    runner._set_log_directory()
    script_file = runner._prepare_batch_job_script('echo hello world')
    assert 'batch_job_script' in script_file
    assert 'hello world' in runner.run_command(f'cat {script_file}').stdout.strip()


@requires_ssh
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_parse_log_file(runner):
    runner._set_log_directory()
    runner._set_log_file()
    runner.run_command(f"echo '{sample_log_file_contents[0]}' > {runner.log_file}")
    for line in sample_log_file_contents[1:]:
        runner.run_command(f"echo '{line}' >> {runner.log_file}")
    out = runner._parse_log_file()
    assert out == {
        'hostname': 'eniac01',
        'port': '59628',
        'token': 'Loremipsumdolorsitamet',
        'url': 'http://eniac01:59628/?token=Loremipsumdolorsitamet',
    }


@requires_ssh
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
@pytest.mark.parametrize('environment', ['jupyter-forward-dev', None])
def test_conda_activate_cmd(runner, environment):
    if ON_GITHUB_ACTIONS and ('csh' in runner.shell or 'zsh' in runner.shell):
        pytest.xfail('Fails on GitHub Actions due to inconsistent shell behavior')
    runner.conda_env = environment
    cmd = runner._conda_activate_cmd()
    assert cmd in ['source activate', 'conda activate']


@requires_ssh
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_conda_activate_cmd_error(runner):
    runner.conda_env = 'DOES_NOT_EXIST'
    with pytest.raises(SystemExit):
        runner._conda_activate_cmd()


@requires_ssh
@pytest.mark.parametrize('runner', SHELLS, indirect=True)
def test_generate_redirect_cmd(runner):
    runner._set_log_directory()
    runner._set_log_file()
    cmd = runner._generate_redirect_command(command='echo "hello world"', log_file=runner.log_file)
    if 'csh' in runner.shell:
        assert cmd.endswith(runner.log_file)
    else:
        assert cmd.endswith(f'{runner.log_file} 2>&1')
