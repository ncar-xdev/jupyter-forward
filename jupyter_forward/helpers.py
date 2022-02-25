from __future__ import annotations

import getpass
import re
import socket
import urllib.parse

from .console import console


def open_browser(port: int = None, token: str = None, url: str = None, path=None) -> None:
    """Opens notebook interface in a new browser window.

    Parameters
    ----------
    port : int, optional
        Port number to use, by default None
    token : str, optional
        token used for authentication, by default None
    url : str, optional
        Notebook url, by default None
    path : str, optional
        Notebook path

    Raises
    ------
    ValueError
        If url is None and port is None
    """

    import webbrowser

    if not url:
        if port is None:
            raise ValueError('Please specify port number to use.')
        url = f'http://localhost:{port}'
        if token:
            url = f'{url}/?token={token}'
        url = f'{url}/lab/tree/{path}' if path else url

    console.rule('[bold green]Opening Jupyter Lab interface in a browser', characters='*')
    console.print(f'Jupyter Lab URL: {url}')
    console.rule('[bold green]', characters='*')
    webbrowser.open(url, new=2)


def is_port_available(port) -> bool:
    socket_for_port_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    status = socket_for_port_check.connect_ex(('localhost', int(port)))
    return status != 0


def parse_stdout(stdout: str) -> dict[str, str]:
    """Parses stdout to determine remote_hostname, port, token, url

    Parameters
    ----------
    stdout : str
        Contents of the log file/stdout

    Returns
    -------
    dict
        A dictionary containing hotname, port, token, and url
    """

    hostname, port, token, url = None, None, None, None
    urls = set(
        re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            stdout,
        )
    )
    for url in urls:
        url = url.strip()
        if '127.0.0.1' not in url:
            result = urllib.parse.urlparse(url)
            hostname, port = result.netloc.split(':')
            if 'token' in result.query:
                token = result.query.split('token=')[-1].strip()
            break
    return {'hostname': hostname, 'port': port, 'token': token, 'url': url}


def _authentication_handler(title, instructions, prompt_list):
    """
    Handler for paramiko auth_interactive_dumb
    """
    return [getpass.getpass(str(pr[0])) for pr in prompt_list]
