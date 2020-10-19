#!/usr/bin/env python
# flake8: noqa
"""Top-level module for jupyter_forward ."""
from pkg_resources import DistributionNotFound, get_distribution

from .core import RemoteRunner

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    _version__ = '0.0.0'  # pragma: no cover
