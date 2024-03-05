# RP2040 with TMF8805 using MicroPython

This code origins from the course [Embedded Systems](https://www.fh-muenster.de/eti/personen/professoren/gloesekoetter/embedded-systems.php) at [FH Münster – University of Applied Sciences](https://www.fh-muenster.de/). There a RP2040 with a TMF8805 programmed with MicroPython was used to measure the water level in a pipe with a swimmer.

## Development

To setup your local development environment install [Visual Studio Code](https://code.visualstudio.com/) and the [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension. After that connect the Raspberry Pi Pico using a USB cabel and run your code using MicroPico. To enforce a global style please install the [development requirements](./dev.requirements.txt) and after that the pre-commit hook using `pre-commit install`.

## Setup & upload project to Pico

- Download the latest firmware from https://micropython.org/download/RPI_PICO/ and flash the RP2040 via UF2 bootloader
- Follow the steps above to setup a local development environment
- Open the command pallete (```CTRL + SHIFT + P```)
- Search for ```MicroPico: Configure project``` and execute it
- Search for ```MicroPico: Upload project to Pico``` and execute it
- Switch to the ```main.py``` and run it!

## TMF8805

To create an instance of the `TMF8805` class you can use the following code snippet:

```python
tmf8805: TMF8805 = TMF8805(
    enable=7,
    sda=4,
    scl=5,
    i2c_frequency=100000,
    debug=True
)
tmf8805.initialize()
distance: float = tmf8805.get_measurement()
print(f"Measured distance: {distance}mm")
```

or copy the contents from `main.py`
