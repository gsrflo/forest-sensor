#!/bin/env python3
#
# Thingstream Click Interface Library
#
# (C) https://gitlab.com/quanten 2020
# Apache License 2.0


import serial
import thingstream_click


class SerialInterfacePySerial(thingstream_click.SerialInterface):

    def __init__(self, port, baudrate, timeout):
        self.pyserial = serial.Serial()
        self.pyserial.port = port
        self.pyserial.baudrate = baudrate
        self.pyserial.timeout = timeout
        super().__init__(port, baudrate, timeout)

    def init(self):
        self.pyserial.open()
        return True

    def available(self):
        return self.pyserial.in_waiting

    def readline(self):
        return self.pyserial.readline().decode("utf-8")

    def write(self, buffer):
        return self.pyserial.write(buffer.encode('utf-8'))

    def deinit(self):
        self.pyserial.close()
