.. image:: https://img.shields.io/github/workflow/status/NCAR/jupyter_forward/CI?logo=github&style=for-the-badge
    :target: https://github.com/NCAR/jupyter_forward/actions
    :alt: GitHub Workflow CI Status

.. image:: https://img.shields.io/github/workflow/status/NCAR/jupyter_forward/code-style?label=Code%20Style&style=for-the-badge
    :target: https://github.com/NCAR/jupyter_forward/actions
    :alt: GitHub Workflow Code Style Status

.. image:: https://img.shields.io/codecov/c/github/NCAR/jupyter_forward.svg?style=for-the-badge
    :target: https://codecov.io/gh/NCAR/jupyter_forward

.. If you want the following badges to be visible, please remove this line, and unindent the lines below
    .. image:: https://img.shields.io/readthedocs/jupyter_forward/latest.svg?style=for-the-badge
        :target: https://jupyter_forward.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

    .. image:: https://img.shields.io/pypi/v/jupyter_forward.svg?style=for-the-badge
        :target: https://pypi.org/project/jupyter_forward
        :alt: Python Package Index

    .. image:: https://img.shields.io/conda/vn/conda-forge/jupyter_forward.svg?style=for-the-badge
        :target: https://anaconda.org/conda-forge/jupyter_forward
        :alt: Conda Version


jupyter-forward
===============

Jupter-forward

1. SSHs into a cluster resource
2. Launches jupyterlab on the cluster and
3. Port forwards jupyter lab session back to your local machine!


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
