#!/usr/bin/env python3
# flake8: noqa
"""Top-level module for jupyter_forward ."""

from pkg_resources import DistributionNotFound, get_distribution

from .core import RemoteRunner

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'unknown'  # pragma: no cover
