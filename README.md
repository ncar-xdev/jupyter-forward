[![GitHub Workflow CI Status](https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/CI?logo=github&style=for-the-badge)](https://github.com/NCAR/jupyter-forward/actions)
[![GitHub Workflow Code Style Status](https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/linting?label=Code%20Style&style=for-the-badge)](https://github.com/NCAR/jupyter-forward/actions)
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
  - [Overview](#overview)
  - [Motivation](#motivation)
  - [Usage](#usage)
    - [SSH Configuration](#ssh-configuration)
    - [Launching Jupyter Lab on a Remote Cluster](#launching-jupyter-lab-on-a-remote-cluster)
  - [Development](#development)

## Overview

Jupyter-forward performs the following tasks:

1. Log into a remote cluster/resource via the SSH protocol.
2. Launch Jupyter Lab on the remote cluster.
3. Port forward Jupyter Lab session back to your local machine!

## Motivation

Jupyter-forward simplifies the process of running `jupyter lab` on a remote machine and allows users to mimic the behavior of the JupyterHub when the that remote machine is down for maintenance.

## Usage

```bash
❯ jupyter-forward --help
Usage: jupyter-forward [OPTIONS] COMMAND [ARGS]...

  Jupyter Lab Port Forwarding Utility

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  config  Prints an ssh configuration for the user, selecting a login node...
  end     Stops the running Jupyter Lab server.
  resume  Resumes an already running remote Jupyter Lab session.
  start   Starts Jupyter lab on a remote resource and port forwards session...
```

### SSH Configuration

The `config` command generates recommended SSH configuration options for a given host.
Before using the `start` command, you should make sure to

1. generate SSH configuration options
   for your cluster host, and
2. put these in your `~/.ssh/config` file.

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
❯ jupyter-forward config cheyenne mariecurie
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

### Launching Jupyter Lab on a Remote Cluster

`jupyter-forward` provides functionality to launch a jupyter lab session on a remote cluster via the `start` command:

```bash
❯ jupyter-forward start --help

Usage: jupyter-forward start [OPTIONS] HOST

  Starts Jupyter lab on a remote resource and port forwards session to local
  machine.

Arguments:
  HOST  [required]

Options:
  --port INTEGER       The port the notebook server will listen on. If not
                       specified, uses a random port  [default: 59628]

  --conda-env TEXT     Name of conda environment that contains jupyter lab
                       [default: base]

  --notebook-dir TEXT  The directory to use for notebooks  [default: $HOME]
  --help               Show this message and exit.
```

For instance, here is how to start a jupyter lab server running on port 9999 on one of Cheyenne's login nodes:

```bash
❯ jupyter-forward start cheyenne --notebook-dir /glade/scratch/mariecurie  --port 9999
```

**Note:** The `start` command will prompt you for your password.

## Development

For a development install, do the following in the repository directory:

```bash
conda env update -f ci/environment.yml
conda activate jupyter-forward-dev
python -m pip install -e .
```

Also, please install `pre-commit` hooks from the root directory of the created project by running::

```bash
pre-commit install
```

These code style pre-commit hooks (black, isort, flake8, ...) will run every time you are about to commit code.
