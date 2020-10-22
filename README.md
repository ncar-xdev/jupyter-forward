# jupyter-forward

- [jupyter-forward](#jupyter-forward)
  - [Badges](#badges)
  - [Overview](#overview)
  - [Usage](#usage)
    - [Running on a Remote Host's Head Node](#running-on-a-remote-hosts-head-node)
    - [Running on a Remote Host's Compute Node](#running-on-a-remote-hosts-compute-node)

## Badges

| CI          | [![GitHub Workflow Status][github-ci-badge]][github-ci-link] [![GitHub Workflow Status][github-lint-badge]][github-lint-link] [![Code Coverage Status][codecov-badge]][codecov-link] |
| :---------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| **Docs**    |                                                                    [![Documentation Status][rtd-badge]][rtd-link]                                                                    |
| **Package** |                                                         [![Conda][conda-badge]][conda-link] [![PyPI][pypi-badge]][pypi-link]                                                         |
| **License** |                                                                        [![License][license-badge]][repo-link]                                                                        |

## Overview

Jupyter-forward simplifies the process of running `jupyter lab` on a remote machine by performing the following tasks on behalf of the users:

1. Log into a remote cluster/resource via the SSH protocol.
2. Launch Jupyter Lab on the remote cluster.
3. Port forward Jupyter Lab session back to your local machine!
4. Opening the port forwarded Jupyter Lab session into your local browser

## Usage

`jupyter-forward` provides functionality to launch a jupyter lab session on a remote cluster via the `jupyter-forward` command:

```bash
❯ jupyter-forward --help                                                                                                      (playground) 18:35:43
Usage: jupyter-forward [OPTIONS] HOST

  Starts Jupyter lab on a remote resource and port forwards session to local
  machine.

Arguments:
  HOST  [required]

Options:
  --port INTEGER                  The local port the remote notebook server
                                  will be forwarded to. If not specified,
                                  defaults to 8888.  [default: 8888]

  --conda-env TEXT                Name of conda environment on the remote host
                                  that contains jupyter lab

  --notebook-dir TEXT             The directory on the remote host to use for
                                  notebooks

  --port-forwarding / --no-port-forwarding
                                  Whether to set up SSH port forwarding or not
                                  [default: True]

  -i, --identity PATH             Selects a file from which the identity
                                  (private key) for public key authentication
                                  is read.

  -c, --launch-command TEXT       Custom command to run before launching
                                  Jupyter Lab. For instance: "qsub -q regular
                                  -l select=1:ncpus=36,walltime=00:05:00 -A
                                  AABD1115"

  --install-completion            Install completion for the current shell.
  --show-completion               Show completion for the current shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
```

### Running on a Remote Host's Head Node

For instance, here is how to start a jupyter lab server running on port 9999 on one of Cheyenne's login nodes:

```bash
❯ jupyter-forward mariecurie@cheyenne.ucar.edu
```

### Running on a Remote Host's Compute Node

To launch `jupyter lab` on a remote host's compute node, the user needs to specify the `--launch-command` option. The launch command is meant to submit a job on the remote host's queueing system. Once the job is up and running, `jupyter lab` is launched on the compute node and the session is port-forwarded to the user's local machine.

Here is a couple examples:

- Launch Jupyter Lab on a remote system that uses [PBS job scheduler](https://www.altair.com/pbs-works-documentation/)

```bash
❯ jupyter-forward mariecurie@cheyenne.ucar.edu --launch-command "qsub -q regular -l select=1:ncpus=36,walltime=00:05:00 -A AABD1115"
```

- Launch Jupyter Lab on a remote system that uses [Slurm job scheduler](https://slurm.schedmd.com/documentation.html)

```bash
❯ jupyter-forward mariecurie@casper.ucar.edu --launch-command "sbatch -A AABD1115 -t 00:05:00"
```

[github-ci-badge]: https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/CI?label=CI&logo=github&style=for-the-badge
[github-lint-badge]: https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/linting?label=linting&logo=github&style=for-the-badge
[github-ci-link]: https://github.com/NCAR/jupyter-forward/actions?query=workflow%3ACI
[github-lint-link]: https://github.com/NCAR/jupyter-forward/actions?query=workflow%3Alinting
[codecov-badge]: https://img.shields.io/codecov/c/github/NCAR/jupyter-forward.svg?logo=codecov&style=for-the-badge
[codecov-link]: https://codecov.io/gh/NCAR/jupyter-forward
[rtd-badge]: https://img.shields.io/readthedocs/jupyter-forward/latest.svg?style=for-the-badge
[rtd-link]: https://jupyter-forward.readthedocs.io/en/latest/?badge=latest
[pypi-badge]: https://img.shields.io/pypi/v/jupyter-forward?logo=pypi&style=for-the-badge
[pypi-link]: https://pypi.org/project/jupyter-forward
[conda-badge]: https://img.shields.io/conda/vn/conda-forge/jupyter-forward?logo=anaconda&style=for-the-badge
[conda-link]: https://anaconda.org/conda-forge/jupyter-forward
[license-badge]: https://img.shields.io/github/license/NCAR/jupyter-forward?style=for-the-badge
[repo-link]: https://github.com/NCAR/jupyter-forward
