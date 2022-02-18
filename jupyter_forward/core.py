from __future__ import annotations

import dataclasses
import datetime
import getpass
import pathlib
import socket
import sys
import time

import invoke
import paramiko
from fabric import Connection

from .console import console
from .helpers import _authentication_handler, is_port_available, open_browser, parse_stdout

timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')


@dataclasses.dataclass
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
    notebook: str = None
    port_forwarding: bool = True
    launch_command: str = None
    identity: str = None
    shell: str = None

    def __post_init__(self):
        if self.notebook_dir is not None and self.notebook is not None:
            raise ValueError('`notebook_dir` and `notebook` are mutually exclusive')
        if self.notebook:
            self.notebook = pathlib.Path(self.notebook)
            self.notebook_dir = str(self.notebook.parent)
            self.notebook = self.notebook.name

        if self.port_forwarding and not is_port_available(self.port):
            console.print(
                f'''[bold red]Specified port={self.port} is already in use on your local machine. Try a different port'''
            )
            sys.exit(1)
        self._authenticate()

    def _authenticate(self):
        console.rule('[bold green]Authentication', characters='*')

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

    def _check_shell(self):
        if self.shell is None:
            shell = self.session.run('echo $SHELL', hide='out').stdout.strip()
            if not shell:
                raise ValueError('Could not determine shell. Please specify one using --shell.')
            self.shell = shell
        console.print(f'[bold cyan]Using shell: {self.shell}')

    def run_command(
        self,
        command,
        exit=True,
        warn=True,
        pty=True,
        hide=None,
        echo=True,
        **kwargs,
    ):
        command = f'''{self.shell} -c "{command}"'''
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
            open_browser(port=local_port, token=self.parsed_result['token'], path=self.notebook)
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
        self._check_shell()
        check_jupyter_status = 'command -v jupyter'
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
        self._set_log_directory()
        self._set_log_file()
        command = r'jupyter lab --no-browser --ip=\$(hostname -f)'
        if self.notebook_dir:
            command = f'{command} --notebook-dir={self.notebook_dir}'
        command = f'{command} > {self.log_file} 2>&1'
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
        self.session.run(f'{self.shell} -c "{command}"', asynchronous=True, pty=True, echo=True)

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
            open_browser(url=self.parsed_result['url'], path=self.notebook)
            self.run_command(command=f'tail -f {self.log_file}')

    def _set_log_file(self):
        log_file = f'{self.log_dir}/log_{timestamp}.txt'
        self.run_command(command=f'touch {log_file}')
        self.log_file = log_file
        console.print(f'[bold cyan]:white_check_mark: Log file is set to {log_file}')
        return self

    def _set_log_directory(self):
        def _check_log_file_dir(directory):
            check_dir_command = f"touch {directory}/foobar && rm -rf {directory}/foobar && echo '{directory} is WRITABLE' || echo '{directory} is NOT WRITABLE'"
            _tmp_dir_status = self.run_command(command=check_dir_command, exit=False)
            return directory if 'is WRITABLE' in _tmp_dir_status.stdout.strip() else None

        console.rule(f'[bold green] Creating log file on {self.session.host}', characters='*')
        # TODO: Allow users to override this via a `--log-dir`
        log_dir = None
        tmp_dir_env_status = self.run_command(command='printenv TMPDIR', exit=False)
        home_dir_env_status = self.run_command(command='printenv HOME', exit=False)
        if not tmp_dir_env_status.failed:
            log_dir = _check_log_file_dir(tmp_dir_env_status.stdout.strip())
        elif not home_dir_env_status.failed:
            log_dir = _check_log_file_dir(home_dir_env_status.stdout.strip())
        else:
            tmp_dir_error_message = '$TMPDIR is not defined'
            home_dir_error_message = '$HOME is not defined'
            console.print(
                f'[bold red]Can not determine directory for log file:\n{home_dir_error_message}\n{tmp_dir_error_message}'
            )
            sys.exit(1)
        log_dir = f'{log_dir}/.jupyter_forward'
        self.run_command(command=f'mkdir -p {log_dir}')
        console.print(f'[bold cyan]:white_check_mark: Log directory is set to {log_dir}')
        self.log_dir = log_dir
        return self
