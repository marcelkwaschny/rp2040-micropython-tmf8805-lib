"""Library for the tmf8805 sensor"""

import sys

import utime
from machine import I2C, WDT, Pin

# Constants definitions
DEFAULT_I2C_ADDR = "0x41"
CPU_READY_TIMEOUT = 200
APPLICATION_READY_TIMEOUT = 500
DATA_AVAILABLE_TIMEOUT = 500
CHIP_ID_NUMBER = "0x07"
APPLICATION = "0xc0"
BOOTLOADER = "0x80"
COMMAND_CALIBRATION = "0x0b"
COMMAND_FACTORY_CALIBRATION = "0x0a"
COMMAND_MEASURE = "0x02"
COMMAND_RESULT = "0x55"
COMMAND_SERIAL = "0x47"
COMMAND_STOP = "0xff"
INTERRUPT_MASK = "0x01"
CONTENT_CALIBRATION = "0x0a"

# Values below were taken from AN000597, pp 22
ALGO_STATE = [
    "0xB1",
    "0xA9",
    "0x02",
    "0x00",
    "0x00",
    "0x00",
    "0x00",
    "0x00",
    "0x00",
    "0x00",
    "0x00",
]

# Error constants
ERROR_NONE = "0x00"
ERROR_I2C_COMM_ERROR = "0x01"
ERROR_CPU_RESET_TIMEOUT = "0x02"
ERROR_WRONG_CHIP_ID = "0x03"
ERROR_CPU_LOAD_APPLICATION_ERROR = "0x04"
ERROR_FACTORY_CALIBRATION_ERROR = "0x05"

# GPIO mode
MODE_INPUT = "0x00"
MODE_LOW_INPUT = "0x01"
MODE_HIGH_INPUT = "0x02"
MODE_VCSEL = "0x03"
MODE_LOW_OUTPUT = "0x04"
MODE_HIGH_OUTPUT = "0x05"

# COMMAND constants
CMD_DATA_7 = "0x00"
CMD_DATA_6 = "0x01"
CMD_DATA_5 = "0x02"
CMD_DATA_4 = "0x03"
CMD_DATA_3 = "0x04"
CMD_DATA_2 = "0x05"
CMD_DATA_1 = "0x06"
CMD_DATA_0 = "0x07"

# CPU status
CPU_RESET = "0x07"
CPU_READY = "0x06"

# Registers definitions
REGISTER_APPID = "0x00"
REGISTER_APPREQID = "0x02"
REGISTER_APPREV_MAJOR = "0x01"
REGISTER_APPREV_MINOR = "0x12"
REGISTER_APPREV_PATCH = "0x13"
REGISTER_CMD_DATA9 = "0x06"
REGISTER_CMD_DATA8 = "0x07"
REGISTER_CMD_DATA7 = "0x08"
REGISTER_CMD_DATA6 = "0x09"
REGISTER_CMD_DATA5 = "0x0A"
REGISTER_CMD_DATA4 = "0x0B"
REGISTER_CMD_DATA3 = "0x0C"
REGISTER_CMD_DATA2 = "0x0D"
REGISTER_CMD_DATA1 = "0x0E"
REGISTER_CMD_DATA0 = "0x0F"
REGISTER_COMMAND = "0x10"
REGISTER_PREVIOUS = "0x11"
REGISTER_STATUS = "0x1D"
REGISTER_REGISTER_CONTENTS = "0x1E"
REGISTER_TID = "0x1F"
REGISTER_RESULT_NUMBER = "0x20"
REGISTER_RESULT_INFO = "0x21"
REGISTER_DISTANCE_PEAK_0 = "0x22"
REGISTER_DISTANCE_PEAK_1 = "0x23"
REGISTER_SYS_CLOCK_0 = "0x24"
REGISTER_SYS_CLOCK_1 = "0x25"
REGISTER_SYS_CLOCK_2 = "0x26"
REGISTER_SYS_CLOCK_3 = "0x27"
REGISTER_STATE_DATA_0 = "0x28"
REGISTER_STATE_DATA_1 = "0x29"
REGISTER_STATE_DATA_2 = "0x2A"
REGISTER_STATE_DATA_3 = "0x2B"
REGISTER_STATE_DATA_4 = "0x2C"
REGISTER_STATE_DATA_5 = "0x2D"
REGISTER_STATE_DATA_6 = "0x2E"
REGISTER_STATE_DATA_7 = "0x2F"
REGISTER_STATE_DATA_8_XTALK_MSB = "0x30"
REGISTER_STATE_DATA_9_XTALK_LSB = "0x31"
REGISTER_STATE_DATA_10_TJ = "0x32"
REGISTER_REFERENCE_HITS_0 = "0x33"
REGISTER_REFERENCE_HITS_1 = "0x34"
REGISTER_REFERENCE_HITS_2 = "0x35"
REGISTER_REFERENCE_HITS_3 = "0x36"
REGISTER_OBJECT_HITS_0 = "0x37"
REGISTER_OBJECT_HITS_1 = "0x38"
REGISTER_OBJECT_HITS_2 = "0x39"
REGISTER_OBJECT_HITS_3 = "0x3A"
REGISTER_FACTORY_CALIB_0 = "0x20"
REGISTER_STATE_DATA_WR_0 = "0x2E"
REGISTER_ENABLE_REG = "0xE0"
REGISTER_INT_STATUS = "0xE1"
REGISTER_INT_ENAB = "0xE2"
REGISTER_ID = "0xE3"
REGISTER_REVID = "0xE4"

# Calibration data
CALIBRATION_DATA_LENGTH = 14

# Status constants
MISSING_FACTORY_CALIBRATION = 39


class TMF8805:
    """Implementation for the tmf8805 sensor"""

    enable: int
    sda: int
    scl: int
    address: str
    debug: bool
    i2c: I2C

    def __init__(
        self,
        enable: int,
        sda: int,
        scl: int,
        wdt: WDT,
        address: str = "0x41",
        i2c_id: int = 0,
        i2c_frequency: int = 100000,
        debug: bool = False,
    ):
        self.enable = enable
        self.sda = sda
        self.scl = scl
        self.address = address
        self.debug = debug
        self.wdt = wdt

        self.power_up()
        self.i2c = I2C(i2c_id, sda=Pin(sda), scl=Pin(scl), freq=i2c_frequency)

    def hex_to_dec(self, hex_value: str) -> int:
        """Helper method to convert a hex string to a decimal value

        Args:
            hex_value (str): Hex string that should be converted

        Returns:
            int: Converted decimal as an integer
        """

        return int(hex_value, 0)

    def is_connected(self) -> bool:
        """Scans the I2C bus and checks if the given address is found

        Returns:
            bool: True if the address could be found, False otherwise
        """

        devices = self.i2c.scan()

        return self.hex_to_dec(self.address) in devices

    def read_single_byte(self, register: str) -> int:
        """Reads a single bytes from a given register

        Args:
            register (str): Register that should be read

        Returns:
            int: Read value as a decimal
        """

        value = self.i2c.readfrom_mem(
            self.hex_to_dec(self.address), self.hex_to_dec(register), 1
        )

        return int.from_bytes(value, sys.byteorder)

    def read_bytes(self, register: str, byte_count: int) -> bytes:
        """Reads the given count of bytes from a given register

        Args:
            register (str): Register that should be read
            byte_count (int): Count of bytes

        Returns:
            bytes: Read content as bytes
        """

        value: bytes = self.i2c.readfrom_mem(
            self.hex_to_dec(self.address), self.hex_to_dec(register), byte_count
        )

        return value

    def write_bytes(self, register: str, value: str):
        """Writes the given value into a given register

        Args:
            register (str): Register in which should be written
            value (str): Value as hex string
        """

        if value.startswith("0x"):
            value = value[2:]

        if len(value) == 1:
            value = "".join(["0", value])

        self.i2c.writeto_mem(
            self.hex_to_dec(self.address),
            self.hex_to_dec(register),
            bytes.fromhex(value),
        )

    def set_register_bit(self, register: str):
        """Sets a 1 in a given register

        Args:
            register (str): Register that should be set to 1
        """

        self.i2c.writeto_mem(
            self.hex_to_dec(self.address), self.hex_to_dec(register), b"1"
        )

    def is_bit_set(self, register: str, position: str) -> bool:
        """Checks if a bit is set in a given register and position

        Args:
            register (str): Register that should be checked
            position (str): Position within the register

        Returns:
            bool: True if the bit is set, False otherwise
        """

        value = int(self.read_single_byte(register))
        mask = 1 << self.hex_to_dec(position)

        return bool(value & mask)

    def reset_cpu(self):
        """Sets the bit in a register so that the cpu reset is triggered"""

        self.set_register_bit(REGISTER_ENABLE_REG)

    def is_cpu_ready(self):
        """Checks if the register that indicates if the cpu is ready for commands is set"""

        counter: int = 0
        ready: bool = False

        self.wdt.feed()
        while counter < CPU_READY_TIMEOUT and not ready:
            ready = self.is_bit_set(REGISTER_ENABLE_REG, CPU_READY)
            self.wdt.feed()

            if not ready:
                counter += 1
                utime.sleep_ms(100)
                self.wdt.feed()

        return ready

    def get_status(self) -> tuple[str, str]:
        """Returns the current status of the sensor

        Returns:
            tuple[str, str]: Tuple with error and description
        """

        status = self.read_single_byte(REGISTER_STATUS)

        if status == MISSING_FACTORY_CALIBRATION:
            return (
                "ErrMissingFactCal",
                "There is no (or no valid) factory calibration on the device. Using default values instead.",
            )

        return f"{status}", "N/A"

    def get_current_calibration(self) -> bytes:
        calibration: bytes = self.read_bytes(
            REGISTER_FACTORY_CALIB_0, CALIBRATION_DATA_LENGTH
        )

        return calibration

    def perform_calibration(self) -> bytes:
        calibration_data: bytes = b""

        self.wdt.feed()
        self.enable_interrupt()
        self.write_bytes(REGISTER_COMMAND, COMMAND_FACTORY_CALIBRATION)

        start_of_calibration = utime.time()

        while (utime.time() - start_of_calibration) < 30:
            self.wdt.feed()
            utime.sleep_ms(50)
            value = self.read_single_byte(REGISTER_REGISTER_CONTENTS)
            print(f"REGISTER_REGISTER_CONTENTS: {value}")

            if value == self.hex_to_dec(CONTENT_CALIBRATION):
                self.wdt.feed()
                utime.sleep_ms(10)
                calibration_data = self.read_bytes(
                    REGISTER_FACTORY_CALIB_0, CALIBRATION_DATA_LENGTH
                )
                break

        return calibration_data

    def set_calibration(self, calibration_data: bytes):
        self.write_bytes(REGISTER_COMMAND, COMMAND_CALIBRATION)
        self.i2c.writeto_mem(
            self.hex_to_dec(self.address),
            self.hex_to_dec(REGISTER_FACTORY_CALIB_0),
            calibration_data,
        )
        self.write_bytes(
            REGISTER_STATE_DATA_WR_0, "".join(entry[2:] for entry in ALGO_STATE)
        )

    def load_measurement_application(self):
        """Sets the values in the register that is responsible for the current loaded application
        to the application to start a measurement
        """

        self.write_bytes(REGISTER_APPREQID, APPLICATION)

    def is_application_ready(self) -> bool:
        """Checks if the current loaded application is ready for execution

        Returns:
            bool: True if the application is ready, False otherwise
        """

        counter: int = 0
        ready: bool = False

        while counter < APPLICATION_READY_TIMEOUT and not ready:
            ready = self.read_single_byte(REGISTER_APPID) == self.hex_to_dec(
                APPLICATION
            )
            self.wdt.feed()

            if not ready:
                counter += 1
                utime.sleep_ms(100)
                self.wdt.feed()

        return ready

    def start_measurement_application(self):
        """Sets the register to start the measurement application"""

        self.write_bytes(REGISTER_COMMAND, COMMAND_MEASURE)

    def is_data_available(self) -> bool:
        """Checks if the data register contains values that could be read

        Returns:
            bool: True if data is available, False otherwise
        """

        counter: int = 0
        data_available: bool = False

        while counter < DATA_AVAILABLE_TIMEOUT and not data_available:
            self.wdt.feed()
            result = self.read_single_byte(REGISTER_REGISTER_CONTENTS)
            data_available = result == int(COMMAND_RESULT, 0)

            if not data_available:
                counter += 1
                utime.sleep_ms(10)
                self.wdt.feed()

        return data_available

    def clear_interrupt_flag(self):
        """Clears the register that is responsible for the interrupt"""

        value = self.read_single_byte(REGISTER_INT_STATUS)
        value = value | int(INTERRUPT_MASK, 0)
        self.write_bytes(REGISTER_INT_STATUS, str(value))

    def enable_interrupt(self):
        """Enables the interrupt of the sensor"""

        value = self.read_single_byte(REGISTER_INT_STATUS)
        value = value | int(INTERRUPT_MASK, 0)
        self.write_bytes(REGISTER_INT_ENAB, str(value))

    def power_down(self):
        """Powers down the sensor"""

        enable_pin = Pin(self.enable, mode=Pin.OUT)
        enable_pin.low()

    def power_up(self):
        """Powers up the sensor"""

        enable_pin = Pin(self.enable, mode=Pin.OUT)
        enable_pin.high()
        self.wdt.feed()

    def initialize(self) -> bool:
        """Initialization of the sensor

        Returns:
            bool: True if initialization was successful, False otherwise
        """

        if not self.is_connected():
            print("TMF8805 is not connected. Please check the parameters")
            return False

        self.reset_cpu()

        if not self.is_cpu_ready():
            print("Waiting for CPU to be ready timed out")
            return False

        return True

    def get_measurement(self) -> int:
        """Loads the application to start a measurement. Wait till the application is ready. Executes the
        measurement application. Waits till data is available. Returns the read data.

        Returns:
            int: Measured distance in mm
        """

        self.load_measurement_application()

        if not self.is_application_ready():
            print("Waiting for measurement application to be ready timed out")
            return False

        self.start_measurement_application()
        self.enable_interrupt()

        if not self.is_data_available():
            print("[TMF8805.Error] Waiting for data to be available timed out")
            return False

        self.wdt.feed()
        result_info = bin(self.read_single_byte(REGISTER_RESULT_INFO))
        result_info = result_info[2:]
        result_info = "".join(reversed(result_info))
        result_info = (lambda s, n, c: s + c * (n - len(s)))(result_info, 8, "0")
        reliabilty = int(result_info[:6], 2)
        status = int(result_info[6:8], 2)
        self.wdt.feed()

        peak_1 = self.read_single_byte(REGISTER_DISTANCE_PEAK_1)
        peak_0 = self.read_single_byte(REGISTER_DISTANCE_PEAK_0)

        distance = peak_1
        distance = distance << 8
        distance += peak_0
        self.wdt.feed()

        if self.debug:
            print(
                f"[TMF8805] Measurement: {distance}mm (Reliabilty: {reliabilty}; Status: {status}; Peak1: {peak_1}; Peak0: {peak_0})"
            )

        return distance
