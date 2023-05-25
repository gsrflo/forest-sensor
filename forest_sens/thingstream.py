#!/bin/env python3
#
# Thingstream Click Interface Library
#
# (C) https://gitlab.com/quanten 2020
# Apache License 2.0


from forest_sens.thingstream_click import ThingstreamClick
from forest_sens.thingstream_click import SerialInterfaceThingstreamDummy


def main():
    serial_interface = SerialInterfaceThingstreamDummy("/dev/ttyACM3", 115200, 10)
    click = ThingstreamClick(serial_interface, debug_mode=True)
    click.init()
    click.at_iot_create()
    print(click.at_iot_info())
    print(click.get_gnss_info(5, True))

if __name__ == "__main__":
    main()

