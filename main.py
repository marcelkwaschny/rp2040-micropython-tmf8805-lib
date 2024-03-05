import machine

from tmf8805.tmf8805 import TMF8805

if __name__ == "__main__":
    tmf8805: TMF8805 = TMF8805(
        enable=7,
        sda=4,
        scl=5,
        i2c_frequency=100000,
        debug=True,
        wdt=machine.WDT(timeout=8000),
    )

    while True:
        tmf8805.initialize()
        distance: int = tmf8805.get_measurement()
        print(f"Distance: {distance}mm")
