# jupyter-forward

| CI          | [![GitHub Workflow Status][github-ci-badge]][github-ci-link] [![Code Coverage Status][codecov-badge]][codecov-link] [![pre-commit.ci status][pre-commit.ci-badge]][pre-commit.ci-link] |
| :---------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| **Docs**    |                                                                     [![Documentation Status][rtd-badge]][rtd-link]                                                                     |
| **Package** |                                                          [![Conda][conda-badge]][conda-link] [![PyPI][pypi-badge]][pypi-link]                                                          |
| **License** |                                                                         [![License][license-badge]][repo-link]                                                                         |

## Overview

Jupyter-forward simplifies the process of running `jupyter lab` on a remote machine by performing the following tasks on behalf of the users:

1. Logging into a remote cluster/resource via the SSH protocol.
2. Launching Jupyter Lab on the remote cluster.
3. Port forwarding Jupyter Lab session back to your local machine.
4. Opening the port forwarded Jupyter Lab session in your local browser.

## Installation

Jupyter-forward can be installed from PyPI with pip:

```bash
python -m pip install jupyter-forward
```

Jupyter-forward is also available from conda-forge for conda installations:

```bash
conda install -c conda-forge jupyter-forward
```

See [documentation](https://jupyter-forward.readthedocs.io) for more information.

[github-ci-badge]: https://github.com/ncar-xdev/jupyter-forward/actions/workflows/ci.yaml/badge.svg
[github-ci-link]: https://github.com/ncar-xdev/jupyter-forward/actions/workflows/ci.yaml
[codecov-badge]: https://img.shields.io/codecov/c/github/ncar-xdev/jupyter-forward.svg?logo=codecov
[codecov-link]: https://codecov.io/gh/ncar-xdev/jupyter-forward
[rtd-badge]: https://readthedocs.org/projects/jupyter-forward/badge/?version=latest
[rtd-link]: https://jupyter-forward.readthedocs.io/en/latest/?badge=latest
[pypi-badge]: https://img.shields.io/pypi/v/jupyter-forward?logo=pypi
[pypi-link]: https://pypi.org/project/jupyter-forward
[conda-badge]: https://img.shields.io/conda/vn/conda-forge/jupyter-forward?logo=anaconda
[conda-link]: https://anaconda.org/conda-forge/jupyter-forward
[license-badge]: https://img.shields.io/github/license/ncar-xdev/jupyter-forward
[repo-link]: https://github.com/ncar-xdev/jupyter-forward
[pre-commit.ci-badge]: https://results.pre-commit.ci/badge/github/ncar-xdev/jupyter-forward/main.svg
[pre-commit.ci-link]: https://results.pre-commit.ci/latest/github/ncar-xdev/jupyter-forward/main
