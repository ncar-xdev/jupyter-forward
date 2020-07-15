[![GitHub Workflow CI Status](https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/CI?logo=github&style=for-the-badge)](https://github.com/NCAR/jupyter-forward/actions)
[![GitHub Workflow Code Style Status](https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/code-style?label=Code%20Style&style=for-the-badge)](https://github.com/NCAR/jupyter-forward/actions)
[![codecov](https://img.shields.io/codecov/c/github/NCAR/jupyter-forward.svg?style=for-the-badge)](https://codecov.io/gh/NCAR/jupyter-forward)


<!--
.. If you want the following badges to be visible, please remove this line, and unindent the lines below
    .. image:: https://img.shields.io/readthedocs/jupyter-forward/latest.svg?style=for-the-badge
        :target: https://jupyter-forward.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

    .. image:: https://img.shields.io/pypi/v/jupyter-forward.svg?style=for-the-badge
        :target: https://pypi.org/project/jupyter-forward
        :alt: Python Package Index

    .. image:: https://img.shields.io/conda/vn/conda-forge/jupyter-forward.svg?style=for-the-badge
        :target: https://anaconda.org/conda-forge/jupyter-forward
        :alt: Conda Version

-->

# jupyter-forward

- [jupyter-forward](#jupyter-forward)
  - [What is this?](#what-is-this)
  - [Usage](#usage)
    - [SSH configuration](#ssh-configuration)
  - [Development](#development)


## What is this?


Jupyter-forward

1. SSHs into a cluster resource
2. Launches jupyterlab on the cluster and
3. Port forwards jupyter lab session back to your local machine!


## Usage

```bash
❯ jupyter-forward --help
Usage: jupyter-forward [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  config  Prints an ssh configuration for the user, selecting a login node...
  start   Jupyter lab/notebook Port Forwarding Utility
```

### SSH configuration

The `config` command generates recommended SSH configuration options for a given host.
Before using the `start` command, you should make sure to generate SSH configuration options
for your cluster host, and putting these in your `~/.ssh/config` file.

```bash
❯ jupyter-forward config --help

Usage: jupyter-forward config [OPTIONS] HOST USERNAME

  Prints an ssh configuration for the user, selecting a login node at random
  if host has multiple login nodes.

Arguments:
  HOST      [required]
  USERNAME  [required]

Options:
  --hostname TEXT
  --help           Show this message and exit.

```

As an example, here is how you can generate SSH configuration for Cheyenne:

```bash
> jupyter-forward config cheyenne mariecurie
```


```bash
Host cheyenne
    User mariecurie
    Hostname cheyenne2.ucar.edu
    GSSAPIDelegateCredentials yes
    GSSAPIAuthentication yes
    ControlMaster auto
    ControlPersist yes
    ControlPath ~/.ssh/control/%C
```


## Development


For a development install, do the following in the repository directory:

 ```bash
 conda env update -f ci/environment.yml
 conda activate sandbox-devel
 python -m pip install -e .
 ```

Also, please install `pre-commit` hooks from the root directory of the created project by running::

```bash
python -m pip install pre-commit
pre-commit install
```

These code style pre-commit hooks (black, isort, flake8, ...) will run every time you are about to commit code.
