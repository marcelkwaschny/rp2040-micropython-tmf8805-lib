"""Mocked module for the utime library of micropython"""

import time as python_time


def sleep_ms(ms: int) -> None:
    """Mocked sleep_ms method

    Args:
        ms (int): Sleep time in milliseconds
    """

    pass


def time() -> int:
    """Returns the current epoch timestamp

    Returns:
        int: Seconds since epoch
    """

    return int(python_time.time())
