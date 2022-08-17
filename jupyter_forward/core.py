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
                f'''[bold red]:x: Specified port={self.port} is already in use on your local machine. Try a different port'''
            )
            sys.exit(1)
        self._authenticate()
        self._check_shell()

    def _authenticate(self):
        console.rule('[bold green]Authenticating', characters='*')

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
        console.rule('[bold green]Verifying shell location', characters='*')
        if self.shell is None:
            shell = self.session.run('echo $SHELL || echo $0', hide='out').stdout.strip()
            if not shell:
                raise ValueError('Could not determine shell. Please specify one using --shell.')
            self.shell = shell
        else:
            # Get the full path to the shell in case the user specified a shell name
            self.shell = self.run_command(f'which {self.shell}').stdout.strip()
        console.print(f'[bold cyan]:white_check_mark: Using shell: {self.shell}')

    def put_file(self, remote_path, content):
        with self.session.get_transport().open_channel(kind="session") as channel:
            channel.exec_command(f"cat > {remote_path}")
            channel.sendall(content.encode())

    def run_command(
        self,
        command,
        exit=True,
        warn=True,
        pty=True,
        echo=True,
        asynchronous=False,
        **kwargs,
    ):
        if 'csh' in self.shell:
            command = f'''{self.shell} -c "{command}"'''
        else:
            command = f'''{self.shell} -lc "{command}"'''
        out = self.session.run(
            command, warn=warn, pty=pty, echo=echo, asynchronous=asynchronous, **kwargs
        )
        if not asynchronous and exit and out.failed:
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
            console.print(f'[bold red]:x: {exc}')
            self.close()
        finally:
            console.rule(
                f'[bold red]:x: Terminated the network 📡 connection to {self.session.host}',
                characters='*',
            )

    def _get_hostname(self):
        if self.launch_command:
            return r'\$(hostname -f)'
        else:
            return self.session.run('hostname -f').stdout.strip()

    def _launch_jupyter(self):
        conda_activate_cmd = self._conda_activate_cmd()
        self._set_log_directory()
        self._set_log_file()
        command = rf'jupyter lab --no-browser --ip={self._get_hostname()}'
        if self.notebook_dir:
            command = f'{command} --notebook-dir={self.notebook_dir}'
        command = self._generate_redirect_command(command=command, log_file=self.log_file)
        if self.conda_env:
            command = f'{conda_activate_cmd} {self.conda_env} && {command}'

        if self.launch_command:
            command = f'{self.launch_command} {self._prepare_batch_job_script(command)}'

        console.rule('[bold green]Launching Jupyter Lab', characters='*')
        self.run_command(command, asynchronous=True)
        self.parsed_result = self._parse_log_file()

        if self.port_forwarding:
            self.setup_port_forwarding()
        else:
            open_browser(url=self.parsed_result['url'], path=self.notebook)
            self.run_command(command=f'tail -f {self.log_file}')

    def _generate_redirect_command(self, *, log_file: str, command: str) -> str:
        if 'csh' in self.shell:
            return f'{command} >& {log_file}'
        else:
            return f'{command} > {log_file} 2>&1'

    def _conda_activate_cmd(self):
        console.rule(
            '[bold green]Running jupyter sanity checks',
            characters='*',
        )
        check_jupyter_status = 'which jupyter'
        conda_activate_cmd = 'source activate'
        if self.conda_env:
            try:
                self.run_command(f'{conda_activate_cmd} {self.conda_env} && {check_jupyter_status}')
            except SystemExit:
                console.print(
                    f'[bold red]:x: `{conda_activate_cmd}` failed. Trying `conda activate`...'
                )
                self.run_command(f'conda activate {self.conda_env} && {check_jupyter_status}')
                conda_activate_cmd = 'conda activate'
        else:
            self.run_command(check_jupyter_status)
        return conda_activate_cmd

    def _parse_log_file(self):
        # wait for logfile to contain access info, then write it to screen
        condition = True
        stdout = None
        with console.status(
            f'[bold cyan]Parsing {self.log_file} log file on {self.session.host} for jupyter information',
            spinner='weather',
        ):
            # TODO: Ensure this loop doesn't run forever if the log file is not found or empty
            while condition:
                try:
                    result = self.run_command(f'cat {self.log_file}', echo=False, hide='out')
                    if 'is running at:' in result.stdout.strip():
                        condition = False
                        stdout = result.stdout
                except invoke.exceptions.UnexpectedExit:
                    pass
        return parse_stdout(stdout)

    def _prepare_batch_job_script(self, command):
        console.rule('[bold green]Preparing Batch Job script', characters='*')
        script_file = f'{self.log_dir}/batch_job_script_{timestamp}'
        shell = self.shell
        if 'csh' not in shell:
            shell = f'{shell} -l'
        for command in [
            f"echo -n '#!' > {script_file}",
            f'echo {shell} >> {script_file}',
            f"echo '{command}' >> {script_file}",
            f'chmod +x {script_file}',
        ]:
            self.run_command(command=command, exit=True)
        console.print(f'[bold cyan]:white_check_mark: Batch Job script resides in {script_file}')
        return script_file

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
        # Try TMPDIR first if defined
        tmp_dir_env_status = self.run_command(command='printenv TMPDIR', exit=False)
        if not tmp_dir_env_status.failed:
            log_dir = _check_log_file_dir('$TMPDIR')
        else:
            # Try HOME if TMPDIR is not defined
            home_dir_env_status = self.run_command(command='printenv HOME', exit=False)
            if not home_dir_env_status.failed:
                log_dir = _check_log_file_dir('$HOME')
            else:
                # Raise an error if neither TMPDIR or HOME are defined
                tmp_dir_error_message = '$TMPDIR is not defined'
                home_dir_error_message = '$HOME is not defined'
                console.print(
                    f'[bold red]:x: Can not determine directory for log file:\n{home_dir_error_message}\n{tmp_dir_error_message}'
                )
                sys.exit(1)
        log_dir = f'{log_dir}/.jupyter_forward'
        self.run_command(command=f'mkdir -p {log_dir}')
        console.print(f'[bold cyan]:white_check_mark: Log directory is set to {log_dir}')
        self.log_dir = log_dir
        return self
