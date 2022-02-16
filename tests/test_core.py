import os
import socket
from unittest import mock as mock

import pytest

import jupyter_forward
from jupyter_forward.core import is_port_available, open_browser, parse_stdout

NOT_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') is None


@pytest.mark.parametrize(
    'stdout, expected',
    [
        (
            """[I 15:46:27.590 LabApp] JupyterLab extension loaded from /jupyterlab\n
            [I 15:46:27.590 LabApp] JupyterLab application directory is /jupyter/lab\n
            [I 15:46:27.594 LabApp] Serving notebooks from local directory: /glade\n
            [I 15:46:27.594 LabApp] The Jupyter Notebook is running at:\n
            [I 15:46:27.594 LabApp] http://eniac01:59628/?token=Loremipsumdolorsitamet\n
            [I 15:46:27.594 LabApp]  or http://127.0.0.1:59628/?token=Loremipsumdolorsitamet\n
            [I 15:46:27.594 LabApp] Use Control-C to stop this server\n
            [C 15:46:27.604 LabApp]\n\n
            To access the notebook, open this file in a browser:\n
            file:///.local/share/jupyter/runtime/nbserver-14905-open.html\n
            Or copy and paste one of these URLs:\n
            http://eniac01:59628/?token=Loremipsumdolorsitamet\n
            or http://127.0.0.1:59628/?token=Loremipsumdolorsitamet\n     """,
            {
                'hostname': 'eniac01',
                'port': '59628',
                'token': 'Loremipsumdolorsitamet',
                'url': 'http://eniac01:59628/?token=Loremipsumdolorsitamet',
            },
        ),
        ('', {'hostname': None, 'port': None, 'token': None, 'url': None}),
    ],
)
def test_parse_stdout(stdout, expected):
    parsed_results = parse_stdout(stdout)
    assert parsed_results == expected


@pytest.mark.parametrize('port', [8888, 9999])
def test_is_port_available(
    port,
):
    @mock.create_autospec
    def connect_ex(self, address):
        # if address[1] == 8888:
        return 0

    with mock.patch.object(socket.socket, 'connect_ex', connect_ex) as m:
        is_port_available(port)
        m.assert_called_once()


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


@pytest.mark.skipif(NOT_GITHUB_ACTIONS, reason='Requires Github Actions environment')
def test_connection():
    USER = os.environ['USER']
    runner = jupyter_forward.RemoteRunner(f'{USER}@eniac.local')
    assert runner.session.is_connected
    assert runner.session.host == '127.0.0.1'
    assert runner.session.user == USER
