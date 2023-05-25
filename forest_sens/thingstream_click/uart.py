#!/bin/env python3
#
# Thingstream Click Interface Library
#
# (C) https://gitlab.com/quanten 2020
# Apache License 2.0

import machine
import thingstream_click

class SerialInterfaceMicroPython(thingstream_click.SerialInterface):

    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        super().__init__(port, baudrate, timeout)

    def init(self):
        self.uart = machine.UART(2)
        self.uart.init(baudrate=self.baudrate, timeout=self.timeout * 1000, timeout_char = 100)
        return True

    def available(self):
        return self.uart.any()

    def readline(self):
        readline = self.uart.readline()
        if readline is not None:
            return readline.decode("utf-8")
        else:
            return ""

    def write(self, buffer):
        self.uart.write(buffer.encode("utf-8"))

    def deinit(self):
        self.uart.deinit()