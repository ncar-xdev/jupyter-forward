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
    return [getpass.getpass(str(pr[0])) for pr in prompt_list]


@dataclass
class RemoteRunner:
    """Starts Jupyter lab on a remote resource and port forwards session to
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
    shell: str = '/usr/bin/sh -l'

    def __post_init__(self):
        console.rule('[bold green]Authentication', characters='*')
        if self.port_forwarding and not is_port_available(self.port):
            console.print(
                f'''[bold red]Specified port={self.port} is already in use on your local machine. Try a different port'''
            )
            sys.exit(1)

        connect_kwargs = {}
        if self.identity:
            connect_kwargs['key_filename'] = [str(self.identity)]

        self.session = Connection(self.host, connect_kwargs=connect_kwargs, forward_agent=True)
        console.print(
            f'[bold cyan]Authenticating user ({self.session.user}) from client ({socket.gethostname()}) to remote host ({self.session.host})'
        )
        # Try passwordless authentication
        try:
            self.session.open()
        except (
            paramiko.ssh_exception.BadAuthenticationType,
            paramiko.ssh_exception.AuthenticationException,
            paramiko.ssh_exception.SSHException,
        ):
            pass

        # Prompt for password and token (2FA)
        if not self.session.is_connected:
            for _ in range(2):
                try:
                    loc_transport = self.session.client.get_transport()
                    try:
                        loc_transport.auth_interactive_dumb(
                            self.session.user, _authentication_handler
                        )
                    except paramiko.ssh_exception.BadAuthenticationType:
                        # It is not clear why auth_interactive_dumb fails in some cases, but
                        # in the examples we could generate auth_password was successful
                        loc_transport.auth_password(self.session.user, getpass.getpass())
                    self.session.transport = loc_transport
                    break
                except Exception:
                    console.log('[bold red]:x: Failed to Authenticate your connection')
        if not self.session.is_connected:
            sys.exit(1)

        console.print('[bold cyan]:white_check_mark: The client is authenticated successfully')

    def run_command(
        self,
        command,
        force_login_shell=False,
        exit=True,
        warn=True,
        pty=True,
        hide=None,
        echo=True,
        **kwargs,
    ):
        command = f'sh -l -c "{command}"' if force_login_shell else command
        out = self.session.run(command, warn=warn, pty=pty, hide=hide, echo=echo, **kwargs)
        if out.failed:
            console.print(f'[bold red] {out.stderr}')
            if exit:
                sys.exit(1)
        return out

    def setup_port_forwarding(self):
        """Sets up SSH port forwarding"""
        console.rule('[bold green]Setting up port forwarding', characters='*')
        local_port = int(self.port)
        remote_port = int(self.parsed_result['port'])
        remote_host = self.parsed_result['hostname']
        console.print(
            f'remote_host: {remote_host}, remote_port: {remote_port}, local_port: {local_port}'
        )
        with self.session.forward_local(
            local_port,
            remote_port=remote_port,
            remote_host=remote_host,
        ):
            time.sleep(
                3
            )  # don't want open_browser to run before the forwarding is actually working
            open_browser(port=local_port, token=self.parsed_result['token'])
            self.run_command(f'tail -f {self.log_file}')

    def close(self):
        self.session.close()

    def start(self):
        """Launches Jupyter Lab on remote host,
        sets up ssh tunnel and opens browser on local machine.

        jupyter lab will pipe output to logfile, which should not exist prior to running
        Logfile will be in $TMPDIR if defined on the remote machine, otherwise in $HOME
        """
        try:
            self._launch_jupyter()
        except Exception as exc:
            console.print(f'[bold red] {exc}')
            self.close()
        finally:
            console.rule(
                '[bold red]Terminated the network 📡 connection to the remote end', characters='*'
            )

    def _launch_jupyter(self):

        console.rule(
            '[bold green]Running jupyter sanity checks (ensuring `jupyter` is in `$PATH`)',
            characters='*',
        )
        check_jupyter_status = 'sh -c "command -v jupyter"'
        conda_activate_cmd = 'source activate'
        if self.conda_env:
            try:
                self.run_command(f'{conda_activate_cmd} {self.conda_env} && {check_jupyter_status}')
            except SystemExit:
                console.print(f'`{conda_activate_cmd}` failed. Trying `conda activate`...')
                self.run_command(f'conda activate {self.conda_env} && {check_jupyter_status}')
                conda_activate_cmd = 'conda activate'

        else:
            self.run_command(check_jupyter_status)
        console.rule(
            f'[bold green] Checking $TMPDIR and $HOME on {self.session.host}', characters='*'
        )
        tmp_dir_env_status = self.run_command(command='printenv TMPDIR', exit=False)
        home_dir_env_status = self.run_command(command='printenv HOME', exit=False)
        check_dir_command = 'touch ${}/foobar && rm -rf ${}/foobar && echo "${} is WRITABLE" || echo "${} is NOT WRITABLE"'
        if not tmp_dir_env_status.failed:
            self._check_log_file_dir(check_dir_command, 'TMPDIR', '$TMPDIR')
        elif not home_dir_env_status.failed:
            self._check_log_file_dir(check_dir_command, 'HOME', '$HOME')
        else:
            tmp_dir_error_message = '$TMPDIR is not defined'
            home_dir_error_message = '$HOME is not defined'
            console.print(
                f'[bold red]Can not determine directory for log file:\n{home_dir_error_message}\n{tmp_dir_error_message}'
            )
            sys.exit(1)
        self.log_dir = f'{self.log_dir}/.jupyter_forward'
        self.run_command(command=f'mkdir -p {self.log_dir}')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        self.log_file = f'{self.log_dir}/log.{timestamp}'
        self.run_command(command=f'touch {self.log_file}')

        command = 'jupyter lab --no-browser --ip=\$(hostname -f)'
        if self.notebook_dir:
            command = f'{command} --notebook-dir={self.notebook_dir}'
        command = f'{command} >& {self.log_file}'
        if self.conda_env:
            command = f'{conda_activate_cmd} {self.conda_env} && {command}'

        if self.launch_command:
            console.rule('[bold green]Preparing Batch Job script', characters='*')
            script_file = f'{self.log_dir}/batch-script.{timestamp}'
            cmd = f"""echo "#!{self.shell}\n\n{command}" > {script_file}"""
            self.run_command(command=cmd)
            self.run_command(command=f'chmod +x {script_file}')
            command = f'{self.launch_command} {script_file}'

        console.rule('[bold green]Launching Jupyter Lab', characters='*')
        self.session.run(f'sh -l -c "{command}"', asynchronous=True, pty=True, echo=True)

        # wait for logfile to contain access info, then write it to screen
        condition = True
        stdout = None
        with console.status(
            f'[bold cyan]Parsing {self.log_file} log file on {self.session.host} for jupyter information',
            spinner='weather',
        ):
            pattern = 'is running at:'
            while condition:
                try:
                    result = self.run_command(f'cat {self.log_file}', echo=False, hide='out')
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
            self.run_command(command=f'tail -f {self.log_file}')

    def _check_log_file_dir(self, check_dir_command, arg1, arg2):
        _tmp_dir_status = self.run_command(
            command=check_dir_command.format(arg1, arg1, arg1, arg1), exit=False
        )

        if 'is WRITABLE' in _tmp_dir_status.stdout.strip():
            self.log_dir = arg2


def open_browser(port: int = None, token: str = None, url: str = None):
    """Opens notebook interface in a new browser window.

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
    console.print(f'Jupyter Lab URL: {url}')
    console.rule('[bold green]', characters='*')
    webbrowser.open(url, new=2)


def is_port_available(port):
    socket_for_port_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    status = socket_for_port_check.connect_ex(('localhost', int(port)))
    return status != 0


def parse_stdout(stdout: str):
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
