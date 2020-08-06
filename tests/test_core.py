import os
import socket
from contextlib import contextmanager
from unittest import mock as mock

import fabric
import pytest
from typer.testing import CliRunner

from jupyter_forward.core import app, open_browser, parse_stdout, setup_port_forwarding

GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS', False)
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


@pytest.mark.parametrize(
    'stdout, expected',
    [
        (
            """[I 15:46:27.590 LabApp] JupyterLab extension loaded from /glade/work/mariecurie/miniconda3/envs/pangeo-bench/lib/python3.7/site-packages/jupyterlab\n
            [I 15:46:27.590 LabApp] JupyterLab application directory is /glade/work/mariecurie/miniconda3/envs/pangeo-bench/share/jupyter/lab\n
            [I 15:46:27.594 LabApp] Serving notebooks from local directory: /glade/scratch/mariecurie\n
            [I 15:46:27.594 LabApp] The Jupyter Notebook is running at:\n
            [I 15:46:27.594 LabApp] http://eniac01:59628/?token=f127c6beb1f4dc902296dbb3ca9de4fd72f1cb737dc1e81c\n
            [I 15:46:27.594 LabApp]  or http://127.0.0.1:59628/?token=f127c6beb1f4dc902296dbb3ca9de4fd72f1cb737dc1e81c\n
            [I 15:46:27.594 LabApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).\n
            [C 15:46:27.604 LabApp]\n\n
            To access the notebook, open this file in a browser:\n
            file:///glade/u/home/mariecurie/.local/share/jupyter/runtime/nbserver-14905-open.html\n
            Or copy and paste one of these URLs:\n
            http://eniac01:59628/?token=f127c6beb1f4dc902296dbb3ca9de4fd72f1cb737dc1e81c\n
            or http://127.0.0.1:59628/?token=f127c6beb1f4dc902296dbb3ca9de4fd72f1cb737dc1e81c\n     """,
            {
                'hostname': 'eniac01',
                'port': '59628',
                'token': 'f127c6beb1f4dc902296dbb3ca9de4fd72f1cb737dc1e81c',
                'url': 'http://eniac01:59628/?token=f127c6beb1f4dc902296dbb3ca9de4fd72f1cb737dc1e81c',
            },
        ),
        ('', {'hostname': None, 'port': None, 'token': None, 'url': None}),
    ],
)
def test_parse_stdout(stdout, expected):
    parsed_results = parse_stdout(stdout)
    assert parsed_results == expected


@pytest.mark.skipif(not GITHUB_ACTIONS, reason='Needs to run as part of the GitHub action workflow')
def test_start():
    _ = runner.invoke(
        app, ['start', 'root@localhost', '--conda-env', 'sandbox-devel', '--port', 9999]
    )


def test_open_browser_exception():
    with pytest.raises(ValueError):
        open_browser(token='ssh')


@pytest.mark.parametrize(
    'port, token, url, expected',
    [
        (9999, 'ssh', None, 'http://localhost:9999/?token=ssh'),
        (None, None, 'http://localhost:9999', 'http://localhost:9999'),
    ],
)
def test_open_browser(port, token, url, expected):
    with mock.patch('webbrowser.open') as mockwebopen:
        open_browser(port, token, url)
        mockwebopen.assert_called_once_with(expected, new=2)


@pytest.mark.parametrize(
    'session, parsed_results, logfile, url',
    [
        (
            fabric.Connection('example.com'),
            {'port': 9999, 'hostname': 'example.com', 'token': 'foobar'},
            'logfile.txt',
            'http://localhost:9999/?token=foobar',
        )
    ],
)
def test_setup_port_forwarding(session, parsed_results, logfile, url):
    @contextmanager
    def forward_local(
        self, local_port, remote_port=None, remote_host='localhost', local_host='localhost'
    ):
        yield

    @mock.create_autospec
    def run(self, command, **kwargs):
        return 'working'

    with mock.patch.object(
        fabric.Connection, 'forward_local', forward_local
    ) as _, mock.patch.object(fabric.Connection, 'run', run) as mockrun, mock.patch(
        'webbrowser.open'
    ) as mockwebopen:
        setup_port_forwarding(session, parsed_results, logfile)
        mockrun.assert_called_once_with(session, 'cat logfile.txt', pty=True)
        mockwebopen.assert_called_once_with(url, new=2)
