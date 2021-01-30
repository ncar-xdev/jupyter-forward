import datetime
import getpass
import socket
import sys
import time
from dataclasses import dataclass

import invoke
import paramiko
from fabric import Connection
from rich.console import Console

console = Console()


def _authentication_handler(title, instructions, prompt_list):
    """
    Handler for paramiko auth_interactive_dumb
    """
    resp = []
    for pr in prompt_list:
        resp.append(getpass.getpass(str(pr[0])))
    return resp


@dataclass
class RemoteRunner:
    """
    Starts Jupyter lab on a remote resource and port forwards session to
    local machine.

    Returns
    -------
    RemoteRunner
        An object that is responsible for connecting to remote host and launching jupyter lab.

    Raises
    ------
    SystemExit
        When the specified local port is not available.
    """

    host: str
    port: int = 8888
    conda_env: str = None
    notebook_dir: str = None
    port_forwarding: bool = True
    launch_command: str = None
    identity: str = None
    shell: str = '/usr/bin/env bash'

    def __post_init__(self):
        if self.port_forwarding and not is_port_available(self.port):
            console.log(
                f'''[bold red]Specified port={self.port} is already in use on your local machine. Try a different port'''
            )
            sys.exit(1)

        connect_kwargs = {}
        if self.identity:
            connect_kwargs['key_filename'] = [self.identity]

        self.session = Connection(self.host, connect_kwargs=connect_kwargs, forward_agent=True)
        console.log(
            f'[bold cyan]Authenticating user ({self.session.user}) from client ({socket.gethostname()}) to remote host ({self.session.host})'
        )
        # Try passwordless authentication
        try:
            self.session.open()
        except (
            paramiko.ssh_exception.BadAuthenticationType,
            paramiko.ssh_exception.AuthenticationException,
        ):
            pass

        # Prompt for password and token (2FA)
        if not self.session.is_connected:
            for _ in range(2):
                try:
                    loc_transport = self.session.client.get_transport()
                    loc_transport.auth_interactive_dumb(self.session.user, _authentication_handler)
                    self.session.transport = loc_transport
                    break
                except Exception:
                    console.log('[bold red]❌ Failed to Authenticate your connection')
            if not self.session.is_connected:
                sys.exit(1)

        console.log('✅ [bold cyan]The client is authenticated successfully')

    def dir_exists(self, directory):
        """
        Checks if a given directory exists on remote host.
        """
        message = "couldn't find the directory"
        cmd = f'''if [[ ! -d "{directory}" ]] ; then echo "{message}"; fi'''
        out = self.session.run(cmd, hide='out').stdout.strip()
        return message not in out

    def setup_port_forwarding(self):
        """
        Sets up SSH port forwarding
        """
        console.rule('[bold green]Setting up port forwarding', characters='*')
        local_port = int(self.port)
        remote_port = int(self.parsed_result['port'])
        with self.session.forward_local(
            local_port,
            remote_port=remote_port,
            remote_host=self.parsed_result['hostname'],
        ):
            time.sleep(
                3
            )  # don't want open_browser to run before the forwarding is actually working
            open_browser(port=local_port, token=self.parsed_result['token'])
            self.session.run(f'tail -f {self.log_file}', pty=True)

    def close(self):
        self.session.close()

    def start(self):
        """
        Launches Jupyter Lab on remote host, sets up ssh tunnel and opens browser on local machine.
        """
        # jupyter lab will pipe output to logfile, which should not exist prior to running
        # Logfile will be in $TMPDIR if defined on the remote machine, otherwise in $HOME

        try:

            if self.dir_exists('$TMPDIR'):
                self.log_dir = '$TMPDIR'
            else:
                self.log_dir = '$HOME'

            self.log_dir = f'{self.log_dir}/.jupyter_forward'
            kwargs = dict(pty=True, shell=self.shell)
            self.session.run(f'mkdir -p {self.log_dir}', **kwargs)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            self.log_file = f'{self.log_dir}/log.{timestamp}'
            self.session.run(f'touch {self.log_file}', **kwargs)

            command = 'jupyter lab --no-browser'
            if self.launch_command:
                command = f'{command} --ip=\$(hostname)'
            else:
                command = f'{command} --ip=`hostname`'

            if self.notebook_dir:
                command = f'{command} --notebook-dir={self.notebook_dir}'

            command = f'{command} > {self.log_file} 2>&1'

            if self.conda_env:
                command = f'conda activate {self.conda_env} && {command}'

            if self.launch_command:
                script_file = f'{self.log_dir}/batch-script.{timestamp}'
                cmd = f"""echo "#!{self.shell}\n\n{command}" > {script_file}"""
                self.session.run(cmd, **kwargs, echo=True)
                self.session.run(f'chmod +x {script_file}', **kwargs)
                command = f'{self.launch_command} {script_file}'

            self.session.run(command, asynchronous=True, **kwargs, echo=False)

            # wait for logfile to contain access info, then write it to screen
            condition = True
            stdout = None
            pattern = 'is running at:'
            with console.status(
                f'[bold cyan]Parsing {self.log_file} log file on {self.session.host} for jupyter information',
                spinner='weather',
            ):
                while condition:
                    try:
                        result = self.session.run(f'cat {self.log_file}', **kwargs, echo=False)
                        if pattern in result.stdout:
                            condition = False
                            stdout = result.stdout
                    except invoke.exceptions.UnexpectedExit:
                        pass
            self.parsed_result = parse_stdout(stdout)

            if self.port_forwarding:
                self.setup_port_forwarding()
            else:
                open_browser(url=self.parsed_result['url'])
                self.session.run(f'tail -f {self.log_file}', **kwargs)
        except Exception:
            self.close()

        finally:
            console.rule(
                '[bold red]Terminated the network 📡 connection to the remote end', characters='*'
            )


def open_browser(port: int = None, token: str = None, url: str = None):
    """
    Opens notebook interface in a new browser window.

    Parameters
    ----------
    port : int, optional
        Port number to use, by default None
    token : str, optional
        token used for authentication, by default None
    url : str, optional
        Notebook url, by default None

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

    console.rule('[bold green]Opening Jupyter Lab interface in a browser', characters='*')
    console.log(f'Jupyter Lab URL: {url}')
    console.rule('[bold green]', characters='*')
    webbrowser.open(url, new=2)


def is_port_available(port):
    socket_for_port_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    status = socket_for_port_check.connect_ex(('localhost', int(port)))
    if status == 0:  # Port is in use
        return False
    return True


def parse_stdout(stdout: str):
    """
    Parses stdout to determine remote_hostname, port, token, url

    Parameters
    ----------
    stdout : str
        Contents of the log file/stdout

    Returns
    -------
    dict
        A dictionary containing hotname, port, token, and url
    """
    import re
    import urllib.parse

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
