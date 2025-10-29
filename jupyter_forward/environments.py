import textwrap
from dataclasses import dataclass
from typing import ClassVar

from .helpers import is_path


@dataclass
class EnvironmentManager:
    manager: str
    path: str | None

    def execution_template(self, script: bool) -> str:
        pass


@dataclass
class Bare(EnvironmentManager):
    def execution_template(self, env: str, script: bool) -> str:
        if script:
            return textwrap.dedent(
                """\
                #!/usr/bin/env {shell}

                {command}
                """
            )
        else:
            return "{shell} '{command}'"


@dataclass
class CondaLike(EnvironmentManager):
    manager: str
    path: str | None = None

    executable_names: ClassVar[list[str]] = ['micromamba', 'mamba', 'conda']

    def execution_template(self, env: str, script: bool) -> str:
        if is_path(env):
            option = f'-p {env}'
        else:
            option = f'-n {env}'

        cmd = self.path if self.path is not None else self.manager

        if script:
            return textwrap.dedent(
                f"""\
                #!/usr/bin/env {{shell}}

                {cmd} run {option} {{command}}
                """.rstrip()
            )
        else:
            return f"{cmd} run {option} {{shell}} '{{command}}'"


@dataclass
class Pixi(EnvironmentManager):
    manager: str = 'pixi'
    path: str | None = None

    def execution_template(self, env: str, script: bool) -> str:
        if ':' in env:
            project, env_name = env.rsplit(':', maxsplit=1)
            option = f'-e {env_name}'
        else:
            project = env
            option = ''

        cmd = self.path if self.path is not None else self.manager

        if script:
            return textwrap.dedent(
                f"""\
                #!/usr/bin/env {{shell}}

                cd "{project}"
                {cmd} run {option} {{command}}
                """.rstrip()
            )
        else:
            return f'cd "{project}" && {cmd} run {option} {{shell}} \'{{command}}\''


environment_managers = {
    'conda': CondaLike,
    'mamba': CondaLike,
    'micromamba': CondaLike,
    'pixi': Pixi,
}
