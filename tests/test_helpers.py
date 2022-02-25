import socket
from unittest import mock

import pytest

import jupyter_forward.helpers

from .misc import sample_log_file_contents


@pytest.mark.parametrize(
    'stdout, expected',
    [
        (
            sample_log_file_contents,
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
    stdout = '\n'.join(stdout)
    parsed_results = jupyter_forward.helpers.parse_stdout(stdout)
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
        jupyter_forward.helpers.is_port_available(port)
        m.assert_called_once()


def test_open_browser_exception():
    with pytest.raises(ValueError):
        jupyter_forward.helpers.open_browser(token='ssh')


@pytest.mark.parametrize(
    'port, token, url, expected',
    [
        (9999, 'ssh', None, 'http://localhost:9999/?token=ssh'),
        (None, None, 'http://localhost:9999', 'http://localhost:9999'),
    ],
)
def test_open_browser(port, token, url, expected):
    with mock.patch('webbrowser.open') as mockwebopen:
        jupyter_forward.helpers.open_browser(port, token, url)
        mockwebopen.assert_called_once_with(expected, new=2)
