# jupyter-forward

- [jupyter-forward](#jupyter-forward)
  - [Badges](#badges)
  - [Overview](#overview)
  - [Installation](#installation)

## Badges

| CI          | [![GitHub Workflow Status][github-ci-badge]][github-ci-link] [![GitHub Workflow Status][github-lint-badge]][github-lint-link] [![Code Coverage Status][codecov-badge]][codecov-link] |
| :---------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| **Docs**    |                                                                    [![Documentation Status][rtd-badge]][rtd-link]                                                                    |
| **Package** |                                                         [![Conda][conda-badge]][conda-link] [![PyPI][pypi-badge]][pypi-link]                                                         |
| **License** |                                                                        [![License][license-badge]][repo-link]                                                                        |

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
