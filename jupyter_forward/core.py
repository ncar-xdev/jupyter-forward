from __future__ import annotations

import contextlib
import dataclasses
import datetime
import getpass
import pathlib
import socket
import sys
import textwrap
import time
from collections.abc import Callable

import invoke
import paramiko
from fabric import Config, Connection

from .console import console
from .helpers import (
    _authentication_handler,
    is_path,
    is_port_available,
    open_browser,
    parse_stdout,
)

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
    env_manager: str | None = None
    env_manager_path: str | None = None
    conda_env: str | None = None
    notebook_dir: str | None = None
    notebook: str | None = None
    port_forwarding: bool = True
    launch_command: str | None = None
    identity: str | None = None
    shell: str | None = None
    auth_handler: Callable = _authentication_handler
    fallback_auth_handler: Callable = getpass.getpass

    def __post_init__(self):
        if self.notebook_dir is not None and self.notebook is not None:
            raise ValueError('`notebook_dir` and `notebook` are mutually exclusive')
        if self.notebook:
            self.notebook = pathlib.Path(self.notebook)
            self.notebook_dir = str(self.notebook.parent)
            self.notebook = self.notebook.name

        if self.port_forwarding and not is_port_available(self.port):
            console.print(
                f"""[bold red]:x: Specified port={self.port} is already in use on your local machine. Try a different port"""
            )
            sys.exit(1)
        self._authenticate()
        self._check_shell()

    def _authenticate(self):
        console.rule('[bold green]Authenticating', characters='*')

        connect_kwargs = {}
        if self.identity:
            connect_kwargs['key_filename'] = [str(self.identity)]

        config = Config(overrides={'run': {'in_stream': False}})
        self.session = Connection(
            self.host, connect_kwargs=connect_kwargs, forward_agent=True, config=config
        )
        console.print(
            f'[bold cyan]Authenticating user ({self.session.user}) from client ({socket.gethostname()}) to remote host ({self.session.host})'
        )
        # Try passwordless authentication
        with contextlib.suppress(
            paramiko.ssh_exception.BadAuthenticationType,
            paramiko.ssh_exception.AuthenticationException,
            paramiko.ssh_exception.SSHException,
        ):
            self.session.open()
        # Prompt for password and token (2FA)
        if not self.session.is_connected:
            for _ in range(2):
                try:
                    loc_transport = self.session.client.get_transport()
                    try:
                        loc_transport.auth_interactive_dumb(self.session.user, self.auth_handler)
                    except paramiko.ssh_exception.BadAuthenticationType:
                        # It is not clear why auth_interactive_dumb fails in some cases, but
                        # in the examples we could generate auth_password was successful
                        loc_transport.auth_password(self.session.user, self.fallback_auth_handler())
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
            if shell := self.session.run('echo $SHELL || echo $0', hide='out').stdout.strip():
                self.shell = shell
            else:
                raise ValueError('Could not determine shell. Please specify one using --shell.')
        else:
            # Get the full path to the shell in case the user specified a shell name
            self.shell = self.run_command(f'which {self.shell}').stdout.strip()
        console.print(f'[bold cyan]:white_check_mark: Using shell: {self.shell}')

    def put_file(self, remote_path, content):
        client = self.session.client
        with client.get_transport().open_channel(kind='session') as channel:
            channel.exec_command(f'cat > {remote_path}')
            channel.sendall(content.encode())

    def _create_template_conda_like(self, script):
        if self.conda_env is not None:
            if is_path(self.conda_env):
                option = f'-p {self.conda_env}'
            else:
                option = f'-n {self.conda_env}'
        else:
            option = ''

        if self.env_manager is None:
            if self._command_exists('micromamba'):
                self.env_manager = 'micromamba'
            elif self._command_exists('mamba'):
                self.env_manager = 'mamba'
            elif self._command_exists('conda'):
                self.env_manager = 'conda'
            else:
                console.print(
                    '[bold red]:x: no conda-like package manager found.'
                    ' Ensure micromamba, mamba, or conda are installed.'
                )
                sys.exit(1)

        if self.env_manager_path is None:
            try:
                self.env_manager_path = self.run_command(f'which {self.env_manager}').stdout.strip()
            except SystemExit:
                console.print(
                    f'[bold red]:x: Could not find {self.env_manager}.'
                    ' Make sure it is in path, or provide an absolute path using `--env-manager-path`.'
                )
                raise

        manager = self.env_manager
        cmd = self.env_manager_path

        console.rule(
            f'[bold green]Running Jupyter sanity checks ({manager})',
            characters='*',
        )
        try:
            self.run_command(f'{cmd} run {option} which jupyter')
        except SystemExit:
            console.print(
                '[bold red]:x: Checking for `jupyter` failed.'
                ' Make sure your environment exists and has `jupyter` installed.'
            )
            raise

        if script:
            return textwrap.dedent(
                f"""\
                #!/usr/bin/env {self.shell}

                {cmd} run {option} {{command}}
                """.rstrip()
            )
        else:
            return f'{cmd} run {option} {{command}}'

    def _create_template_pixi(self, script):
        if self.conda_env is None:
            console.print('[bold red]:x: Pixi global installations are not supported for now.')
            sys.exit(1)

        if ':' in self.conda_env:
            project, env = self.env.rsplit(':', maxsplit=1)
            option = f'-e {env}'
        else:
            project = self.env
            option = ''

        if self.env_manager_path is None:
            try:
                self.env_manager_path = self.run_command('which pixi')
            except SystemExit:
                console.print(
                    '[bold red]:x: Could not find pixi.'
                    ' Make sure it is in path, or provide an absolute path using `--env-manager-path`.'
                )
                raise

        console.rule(
            '[bold green]Running Jupyter sanity checks (pixi)',
            characters='*',
        )

        try:
            self.run_command(f'CWD="{project}" pixi run {option} which jupyter')
        except SystemExit:
            console.print(
                '[bold red]:x: Checking for `jupyter` failed.'
                ' Make sure your environment exists and has `jupyter` installed.'
            )
            raise

        if script:
            return textwrap.dedent(
                f"""\
                #!/usr/bin/env {self.shell}

                cd {project}
                {self.env_manager_path} run {option} {{command}}
                """.rstrip()
            )
        else:
            return f'cd "{project}" && {self.env_manager_path} run {option} {{command}}'

    def _create_template(self, script):
        env_managers = {
            'micromamba': self._create_template_conda_like,
            'mamba': self._create_template_conda_like,
            'conda': self._create_template_conda_like,
            None: self._create_template_conda_like,
            'pixi': self._create_template_pixi,
        }

        template_creator = env_managers.get(self.env_manager)
        if template_creator is None:
            console.print(f'[bold red]:x: Unknown environment manager ({self.env_manager})')
            sys.exit(1)

        return template_creator(script)

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
            return '$(hostname -f)'
        else:
            return self.session.run('hostname -f').stdout.strip()

    def _launch_jupyter(self):
        self._set_log_directory()
        self._set_log_file()
        command = rf'jupyter lab --no-browser --ip={self._get_hostname()}'
        if self.notebook_dir:
            command = f'{command} --notebook-dir={self.notebook_dir}'
        command = self._generate_redirect_command(command=command, log_file=self.log_file)

        if self.launch_command:
            command = f'{self.launch_command} {self._prepare_batch_job_script(command)}'
        else:
            command = self._create_template(script=False).format(command=command)

        from rich.syntax import Syntax

        console.rule('[bold green]Launching Jupyter Lab', characters='*')
        console.print(Syntax(command, 'bash'))
        console.print('[bold yellow]:warning: exiting before executing')
        sys.exit(1)
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

    def _command_exists(self, command: str) -> bool:
        try:
            result = self.run_command(f'which {command}', warn=False, echo=False, exit=False)
            return not result.failed
        except Exception as e:
            console.print(f'[bold yellow]:warning: `{command.lower()}` check failed: {e}')
            return False

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
                with contextlib.suppress(invoke.exceptions.UnexpectedExit):
                    result = self.run_command(f'cat {self.log_file}', echo=False, hide='out')
                    if 'is running at:' in result.stdout.strip():
                        condition = False
                        stdout = result.stdout
        return parse_stdout(stdout)

    def _prepare_batch_job_script(self, command):
        from rich.syntax import Syntax

        console.rule('[bold green]Preparing Batch Job script', characters='*')
        script_file = f'{self.log_dir}/batch_job_script_{timestamp}'
        shell = self.shell
        if 'csh' not in shell:
            shell = f'{shell} -l'

        template = self._create_template(script=True)
        script = template.format(command=command)
        console.print(Syntax(script, 'bash', line_numbers=True))

        self.put_file(script_file, script)
        self.run_command(f'chmod +x {script_file}', exit=True)
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
