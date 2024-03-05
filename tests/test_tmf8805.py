"""Module to test the implementation for the tmf8805 sensor"""

from tests import machine_mock
from tmf8805.tmf8805 import TMF8805


def test_initialization_of_tmf8805(tmf8805_instance: TMF8805):
    """Test if the initialization of the instance is successful"""

    assert tmf8805_instance is not None


def test_connected_check(tmf8805_instance: TMF8805):
    """Test if the is_connected method is working as expected"""

    assert tmf8805_instance.is_connected()

    tmf8805_instance.address = "0x42"
    assert not tmf8805_instance.is_connected()


def test_execution_of_measurement(tmf8805_instance: TMF8805):
    """Test if the performing of a measurement is working"""

    assert tmf8805_instance.initialize()
    distance: int = tmf8805_instance.get_measurement()
    assert distance == 1250


def test_performing_of_calibration(tmf8805_instance: TMF8805):
    """Test if the methods for get, set and perform a calibration are working"""

    machine_mock.TMF8805_MOCK_CONFIGURATION = (
        machine_mock.TMF8805MockConfiguration.PERFORM_CALIBRATION
    )

    current_calibration = tmf8805_instance.get_current_calibration()
    assert current_calibration.decode() == "AAAAAAAAAAAAAA"

    new_calibration = tmf8805_instance.perform_calibration()
    assert new_calibration.decode() == "AAAAAAAAAAAAAA"
    tmf8805_instance.set_calibration(new_calibration)


def test_get_status(tmf8805_instance: TMF8805):
    """Test if the get status method returns a status"""

    error, description = tmf8805_instance.get_status()
    assert error == "ErrMissingFactCal"
    assert (
        description
        == "There is no (or no valid) factory calibration on the device. Using default values instead."
    )


def test_not_implemented_status(tmf8805_instance: TMF8805):
    """Test return of the get status method when a status is not implemented"""

    machine_mock.TMF8805_MOCK_CONFIGURATION = (
        machine_mock.TMF8805MockConfiguration.UNKNOWN_STATUS
    )

    error, description = tmf8805_instance.get_status()
    assert error == "9999"
    assert description == "N/A"


def test_clearing_of_the_interrupt_flag(tmf8805_instance: TMF8805):
    """Test if the clearing of the interrupt flag returns no error"""

    tmf8805_instance.clear_interrupt_flag()


def test_power_up_and_power_down(tmf8805_instance: TMF8805):
    """Test if the power up/down methods don't raise an error"""

    tmf8805_instance.power_down()
    tmf8805_instance.power_up()


def test_sensor_not_connected(tmf8805_instance: TMF8805):
    """Test return from initialization if sensor is not connected"""

    machine_mock.TMF8805_MOCK_CONFIGURATION = (
        machine_mock.TMF8805MockConfiguration.NOT_CONNECTED
    )

    assert not tmf8805_instance.initialize()


def test_cpu_ready_timed_out(tmf8805_instance: TMF8805):
    """Test return from initialization if wait for the cpu to be ready timed out"""

    machine_mock.TMF8805_MOCK_CONFIGURATION = (
        machine_mock.TMF8805MockConfiguration.CPU_READY_TIMEOUT
    )

    assert not tmf8805_instance.initialize()


def test_load_application_timed_out(tmf8805_instance: TMF8805):
    """Test if the timeout of the load application is handled correctly"""

    machine_mock.TMF8805_MOCK_CONFIGURATION = (
        machine_mock.TMF8805MockConfiguration.APPLICATION_READY_TIMEOUT
    )

    assert tmf8805_instance.initialize()
    assert not tmf8805_instance.get_measurement()


def test_data_available_timeout(tmf8805_instance: TMF8805):
    """Test if timeout when waiting for data to be available is handled correctly"""

    machine_mock.TMF8805_MOCK_CONFIGURATION = (
        machine_mock.TMF8805MockConfiguration.DATA_AVAILABLE_TIMEOUT
    )

    assert tmf8805_instance.initialize()
    assert not tmf8805_instance.get_measurement()
