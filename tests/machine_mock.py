"""This module mocks the machine library from micropython"""

import sys
from enum import Enum
from typing import List


class TMF8805MockConfiguration(Enum):
    """Holds the different mock configurations"""

    CORRECT_MEASUREMENT = 0
    PERFORM_CALIBRATION = 1
    NOT_CONNECTED = 2
    CPU_READY_TIMEOUT = 3
    APPLICATION_READY_TIMEOUT = 4
    UNKNOWN_STATUS = 5
    DATA_AVAILABLE_TIMEOUT = 6


TMF8805_MOCK_CONFIGURATION: TMF8805MockConfiguration = (
    TMF8805MockConfiguration.CORRECT_MEASUREMENT
)


class I2C:
    def __init__(self, *args, **kwargs) -> None:
        """Mocks the constructor of the I2C class"""

        pass

    def scan(self) -> List:
        if TMF8805_MOCK_CONFIGURATION == TMF8805MockConfiguration.NOT_CONNECTED:
            return []

        return [65]

    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8) -> bytes:
        if memaddr == 0:  # REGISTER_APPID
            if (
                TMF8805_MOCK_CONFIGURATION
                == TMF8805MockConfiguration.APPLICATION_READY_TIMEOUT
            ):
                return int(0).to_bytes(2, sys.byteorder)

            return int(192).to_bytes(2, sys.byteorder)

        if memaddr == 14:  # REGISTER_ENABLE_REG
            return int(1).to_bytes(2, sys.byteorder)

        if memaddr == 29:  # REGISTER_STATUS
            if TMF8805_MOCK_CONFIGURATION == TMF8805MockConfiguration.UNKNOWN_STATUS:
                return int(9999).to_bytes(
                    2, sys.byteorder
                )  # Status that is not implemented

            return int(39).to_bytes(2, sys.byteorder)  # MISSING_FACTORY_CALIBRATION

        if memaddr == 30:  # REGISTER_REGISTER_CONTENTS
            if (
                TMF8805_MOCK_CONFIGURATION
                == TMF8805MockConfiguration.PERFORM_CALIBRATION
            ):
                return int(10).to_bytes(2, sys.byteorder)

            if (
                TMF8805_MOCK_CONFIGURATION
                == TMF8805MockConfiguration.DATA_AVAILABLE_TIMEOUT
            ):
                return int(0).to_bytes(2, sys.byteorder)

            return int(85).to_bytes(2, sys.byteorder)

        if memaddr == 32:  # REGISTER_FACTORY_CALIB_0
            return ("A" * nbytes).encode()

        if memaddr == 33:  # REGISTER_RESULT_INFO
            return int(63).to_bytes(2, sys.byteorder)  # Reliability = 63, Status = 0

        if memaddr == 34:  # REGISTER_DISTANCE_PEAK_0
            return int(226).to_bytes(2, sys.byteorder)

        if memaddr == 35:  # REGISTER_DISTANCE_PEAK_1
            return int(4).to_bytes(2, sys.byteorder)

        if memaddr == 224:  # REGISTER_ENABLE_REG
            if TMF8805_MOCK_CONFIGURATION == TMF8805MockConfiguration.CPU_READY_TIMEOUT:
                return int(0).to_bytes(2, sys.byteorder)

            return int(64).to_bytes(2, sys.byteorder)

        if memaddr == 225:  # REGISTER_INT_STATUS
            return int(1).to_bytes(2, sys.byteorder)

        pass

    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8) -> None:

        pass


class Pin:
    """Mocks the micropython Pin class"""

    OUT: int = 1

    def __init__(self, *args, **kwargs) -> None:
        """Mocks the constructor of the Pin class"""

        pass

    def high(self) -> None:
        """Mocks the high function of the Pin class"""

        pass

    def low(self) -> None:
        """Mocks the low function of the Pin class"""

        pass


class WDT:
    """Mocks the micropython watchdog class"""

    def __init__(self, *args, **kwargs) -> None:
        """Mocks the constructor of the watchdog class"""

        pass

    def feed(self, *args, **kwargs) -> None:
        """Mocks the feed function of the watchdog"""

        pass
