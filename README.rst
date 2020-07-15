.. image:: https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/CI?logo=github&style=for-the-badge
    :target: https://github.com/NCAR/jupyter-forward/actions
    :alt: GitHub Workflow CI Status

.. image:: https://img.shields.io/github/workflow/status/NCAR/jupyter-forward/code-style?label=Code%20Style&style=for-the-badge
    :target: https://github.com/NCAR/jupyter-forward/actions
    :alt: GitHub Workflow Code Style Status

.. image:: https://img.shields.io/codecov/c/github/NCAR/jupyter-forward.svg?style=for-the-badge
    :target: https://codecov.io/gh/NCAR/jupyter-forward

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


jupyter-forward
===============

What is this?
-------------

Jupyter-forward

1. SSHs into a cluster resource
2. Launches jupyterlab on the cluster and
3. Port forwards jupyter lab session back to your local machine!


Usage
-----

.. code-block::bash

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


.. code-block::bash

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



Development
------------

For a development install, do the following in the repository directory:

.. code-block:: bash

    conda env update -f ci/environment.yml
    conda activate sandbox-devel
    python -m pip install -e .

Also, please install `pre-commit` hooks from the root directory of the created project by running::

      python -m pip install pre-commit
      pre-commit install

These code style pre-commit hooks (black, isort, flake8, ...) will run every time you are about to commit code.
