import pathlib

import pytest

_log_file = pathlib.Path(__file__).parent / 'sample_log_file.txt'


@pytest.fixture
def sample_log_file():
    return _log_file


@pytest.fixture
def sample_log_file_contents():
    with open(_log_file) as f:
        return f.read()
