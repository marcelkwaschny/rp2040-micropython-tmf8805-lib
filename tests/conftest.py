"""This module contains general test configuration"""

import sys

import pytest

from tests import machine_mock, utime_mock

# Mocks the micropython machine module
sys.modules["machine"] = machine_mock

# Mocks the utime module
sys.modules["utime"] = utime_mock

from tmf8805.tmf8805 import TMF8805  # noqa: E402


@pytest.fixture
def tmf8805_instance() -> TMF8805:
    """Fixture for a tmf8805 instance

    Returns:
        TMF8805: The object of a tmf8805 instance
    """

    tmf8805: TMF8805 = TMF8805(
        enable=7, sda=4, scl=5, i2c_frequency=100000, debug=True, wdt=machine_mock.WDT()
    )

    return tmf8805
