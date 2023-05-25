#!/bin/env python3
#
# Thingstream Click Interface Library
#
# (C) https://gitlab.com/quanten 2020
# Apache License 2.0

import time


class ThingstreamClick():
    msg_queue = []

    got_disconnect_msg = False

    def __init__(self, serial_interface, debug_mode=False):
        self.serial_interface = serial_interface
        self.debug_mode = debug_mode

    def init(self):
        """
        Initialise the Serial Interface and try to get the info msg

        :return: True if Serial Interface was successfully initialised and the info msg received
        """
        if self.serial_interface.init():
            info_msg = self.at_iot_info()
            if info_msg == "":
                return False
            else:
                self.__print_debug(info_msg)
                return True
        else:
            return False

    def __parse_msg(self):
        line = self.serial_interface.readline()
        self.__print_debug("received line {line}".format(line=line))
        if line is None or len(line) == 0:
            return (0, "")
        else:
            if line.startswith("+IOTRECEIVE:"):
                self.msg_queue.append(line)
                return (2, "")
            elif line.startswith("+IOTSERVERDISCONNECT: OK"):
                self.got_disconnect_msg = True
                return (2, "")
            elif line.startswith("BUSY"):
                return (4, line)
            elif line.startswith("ERROR"):
                return (8, line)
            else:
                return (1, line)

    def __execute_command(self, command, max_try_to_receive_line=5):
        self.__print_debug("send to uart {str}".format(str=command))
        self.serial_interface.write(command)
        retry_count = 0
        received_msg = (0, "")
        while True:
            received_msg = self.__parse_msg()
            if received_msg[0] == 1:
                break
            elif received_msg[0] == 0:
                retry_count += 1
            elif received_msg[0] == 4 or received_msg[0] == 8:
                break
            if retry_count > max_try_to_receive_line:
                break
        if received_msg[0] != 1:
            self.__print_debug("receive return from command {command} not sucessfull, code {code} and msg {msg}"
                               .format(command=command, code=received_msg[0], msg=received_msg[1]))
        return received_msg[1]

    def __print_debug(self, msg):
        if self.debug_mode:
            print(msg)

    def check_buffer(self):
        """
        Check if something is in the receive buffer of the serial interface
        If there was a IOTRECEIVE it will be pushed into the msg_queue
        """
        if self.serial_interface.available() > 0:
            self.__parse_msg()

    def at_iot_info(self):
        """
        Execute the AT+IOTINFO command

        :return: The return of the IOTINFO
        """
        return self.__execute_command("AT+IOTINFO\r\n")

    def at_iot_cgn_power(self, on):
        """
        Control the GNSS module power

        :param on: True to power the module on, False for of
        :return: True if the action was successful
        """
        return self.__execute_command(
            "AT+IOTCGNSPWR={state}\r\n".format(state=(1 if on else 0))) == '+IOTCGNSPWR: SUCCESS\r\n'

    def at_iot_cgn_get_info(self):
        """
        Execute the AT+IOTCGNSINF command

        :return: The return of IOTCGNSINF
        """
        return self.__execute_command("AT+IOTCGNSINF\r\n")

    def at_iot_create(self):
        """
        Execute AT+IOTCREATE to create the IOT Interface

        :return: True if the action was successful
        """
        return self.__execute_command("AT+IOTCREATE\r\n") == '+IOTCREATE: SUCCESS\r\n'

    def at_iot_connect(self, drop_messages, keep_alive=None):
        """
        Execute AT+IOTCONNECT to connect to the Thingstream Platform

        :param drop_messages: True if a clean session (clearing caches messages) should be requested
        :param keep_alive: Not yet implemented
        :return: True if the action was successful
        """
        if keep_alive is not None:
            # TODO implement keepalive
            self.__print_debug("keep alive not implemented")
        return self.__execute_command("AT+IOTCONNECT={state}\r\n".format(
            state=('true' if drop_messages else 'false'))) == '+IOTCONNECT: SUCCESS\r\n'

    def at_iot_is_connected(self):
        """
        Execute AT+IOTCONNECT? command to check if connected to Thingstream Platform

        :return: True if connected
        """
        return self.__execute_command("AT+IOTCONNECT?\r\n") == '+IOTCONNECT: TRUE\r\n'

    def at_iot_disconnect(self):
        """
        Execute AT+IOTDISCONNECT to disconnect from the Thingstream Platform

        :return: True if the action was successful
        """
        return self.__execute_command("AT+IOTDISCONNECT\r\n") == '+IOTDISCONNECT: SUCCESS\r\n'

    def at_iot_destroy(self):
        """
        Ecxecute the AT+IOTDESTROY command

        :return: True if the action was successfull
        """
        return self.__execute_command("AT+IOTDESTROY\r\n") == '+IOTDESTROY: SUCCESS\r\n'

    def at_iot_publish(self, topic, msg, qos=1, retain=None):
        """
        Execute AT+IOTPUBLISH in order to publish a MQTT message

        :param topic: the MQTT topic
        :param msg: the payload of the message (proper handling of qoutes inside the payload is not know yet and therefore should be avoided)
        :param qos: QOS Level of the Message
        :param retain: not implemented yet
        :return: True if the action was successful
        """
        if retain is not None:
            # TODO implement retain
            self.__print_debug("retain not implemented")
        return self.__execute_command("AT+IOTPUBLISH=\"{topic}\",{qos},\"{msg}\"\r\n".format(topic=topic, qos=qos,
                                                                                             msg=msg)) == '+IOTPUBLISH: SUCCESS\r\n'

    def at_iot_subscribe(self, topic, qos=1):
        """
        Execute AT+IOTSUBSCRIBE in order to subscribe to a MQTT topic

        :param topic: the MQTT topic
        :param qos: QOS Level of incoming messages
        :return: True if the action was successful
        """
        return self.__execute_command(
            "AT+IOTSUBSCRIBE=\"{topic}\",{qos}\r\n".format(topic=topic, qos=qos)) == '+IOTSUBSCRIBE: SUCCESS\r\n'

    def at_iot_unsubscribe(self, topic):
        """
        Execute AT+IOTUNSUBSCRIBE in order to unsubscribe from an MQTT topic

        :param topic: the MQTT topic
        :return: True if the action was successful
        """
        return self.__execute_command(
            "AT+IOTUNSUBSCRIBE=\"{topic}\"\r\n".format(topic=topic)) == '+IOTUNSUBSCRIBE: SUCCESS\r\n'

    def at_iot_reg_pre(self, topic, alias):
        """
        Execute AT+IOTREGPRE to use preregister topics

        :param topic: the MQTT topic
        :param alias: nummerical alias
        :return: True if the action was successful
        """
        return self.__execute_command(
            "AT+IOTREGPRE=\"{topic}\",{alias}\r\n".format(topic=topic, alias=alias)) == '+IOTREGPRE: SUCCESS\r\n'

    def at_iot_sleep(self, minutes):
        """
        Execute AT+IOTSLEEP to sleep

        :param minutes: minutes to sleep
        :return: True if the action was successful
        """
        return self.__execute_command("AT+IOTSLEEP={minutes}\r\n".format(minutes=minutes)) == '+IOTSLEEP: SUCCESS\r\n'

    def at_iot_debug(self, mikrobus=False, usb=False):
        """
        Execute AT+IOTDEBUG to enable debug output from the module

        :param mikrobus: True if debug messages should be outputted to the Mikrobus UART
        :param usb: True if debug messages should be outputted to the USB Interface
        :return: True if the action was successful
        """
        return self.__execute_command(
            "AT+IOTDEBUG={mask}\r\n".format(mask=((1 if mikrobus else 0) + (2 if usb else 0)))) \
               == '+IOTDEBUG: SUCCESS\r\n'

    def at_iot_test(self):
        """
        Execute AT+IOTTEST to test the function

        :return: True if the action was successful
        """
        return self.__execute_command("AT+IOTTEST\r\n") == '+IOTTEST: SUCCESS\r\n'

    def get_gnss_info(self, time_to_wait_for_fix, turn_off_afterwards=True):
        """
        Request information from the GNSS module

        :param time_to_wait_for_fix: seconds to wait after powering on the GNSS before requesting information
        :param turn_off_afterwards: True to turn off the GNSS module after requesting the information
        :return: the output +IOTCGNSINF if successful, empty string otherwise
        """
        self.at_iot_cgn_power(True)
        time.sleep(time_to_wait_for_fix)
        msg = self.at_iot_cgn_get_info()
        if turn_off_afterwards:
            self.at_iot_cgn_power(False)
        if msg.startswith("+IOTCGNSINF:"):
            return msg
        else:
            return ""

    def is_msg_available(self):
        """
        Check messages in the receive queue

        :return: the number of messages in the receive queue
        """
        return len(self.msg_queue) > 0

    def get_msg(self):
        """
        Get a message from the receive queue

        :return: the raw +IOTRECEIVE message if available, empty string otherwise. Subject to change in the future!
        """
        if len(self.msg_queue) > 0:
            return self.msg_queue.pop(0)
        # TODO implement parsing of recevied messages. Regex-use is difficult because of differences between uPy and cPy
        else:
            return ""


class SerialInterface():

    def __init__(self, port, baudrate, timeout):
        """
        creates the object
        :param port: type depends on the implementation
        :param baudrate: baudrate as int
        :param timeout: timeout in seconds
        """
        pass

    def init(self):
        """
        Opens the Serial Port

        :return: True if the init was successful
        """
        return True

    def available(self):
        """
        get Number of available chars

        :return: not negative int. greater 0 if chars are available
        """
        return 0

    def readline(self):
        """
        read on line until a \n
        should be blocking with the timeout specified in the constructor

        :return: the line read, a empty string on timeout
        """
        return ""

    def write(self, buffer):
        """
        Write the string to the serial port
        :param buffer: the string to send
        """
        pass

    def deinit(self):
        """
        Deinit and destroy the Serial Port
        """
        pass


class SerialInterfaceThingstreamDummy(SerialInterface):

    def __init__(self, port, baudrate, timeout):
        super().__init__(port, baudrate, timeout)

    def init(self):
        self.queue = []
        self.created = False
        self.connected = False
        self.cgnpower = False
        return True

    def available(self):
        if len(self.queue) > 0:
            return len(self.queue[0])
        else:
            return 0

    def readline(self):
        return self.queue.pop(0) if len(self.queue) > 0 else ""

    def write(self, buffer):
        if buffer == "AT+IOTCREATE\r\n":
            if not self.created:
                self.created = True
                self.queue.append("+IOTCREATE: SUCCESS\r\n")
            else:
                self.queue.append("+IOTCREATE: ERROR\r\n")
        elif buffer == "AT+IOTDESTROY\r\n":
            if self.created:
                self.created = False
                self.connected = False
                self.queue.append("+IOTDESTROY: SUCCESS\r\n")
            else:
                self.queue.append("+IOTDESTROY: ERROR\r\n")
        elif buffer.startswith("AT+IOTCONNECT="):
            if self.created and not self.connected:
                self.connected = True
                self.queue.append("+IOTCONNECT: SUCCESS\r\n")
            else:
                self.queue.append("+IOTCONNECT: ERROR\r\n")
        elif buffer == "AT+IOTCONNECT?\r\n":
            if self.connected:
                self.queue.append("+IOTCONNECT: TRUE\r\n")
            else:
                self.queue.append("+IOTCONNECT: FALSE\r\n")
        elif buffer == "AT+IOTDISCONNECT\r\n":
            if not self.connected:
                self.connected = False
                self.queue.append("+IOTDISCONNECT: SUCCESS\r\n")
            else:
                self.queue.append("+IOTDISCONNECT: ERROR\r\n")
        elif buffer.startswith("AT+IOTPUBLISH="):
            if self.created and self.connected:
                self.queue.append("+IOTPUBLISH: SUCCESS\r\n")
            else:
                self.queue.append("+IOTPUBLISH: ERROR\r\n")
        elif buffer.startswith("AT+IOTSUBSCRIBE="):
            if self.created and self.connected:
                self.queue.append("+IOTSUBSCRIBE: SUCCESS\r\n")
            else:
                self.queue.append("+IOTSUBSCRIBE: ERROR\r\n")
        elif buffer.startswith("AT+IOTUNSUBSCRIBE="):
            if self.created and self.connected:
                self.queue.append("+IOTUNSUBSCRIBE: SUCCESS\r\n")
            else:
                self.queue.append("+IOTUNSUBSCRIBE: ERROR\r\n")
        elif buffer.startswith("AT+IOTREGPRE="):
            if self.created and not self.connected:
                self.queue.append("+IOTREGPRE: SUCCESS\r\n")
            else:
                self.queue.append("+IOTREGPRE: ERROR\r\n")
        elif buffer.startswith("AT+IOTSLEEP="):
            if self.created and self.connected:
                self.queue.append("+IOTSLEEP: SUCCESS\r\n")
            else:
                self.queue.append("+IOTSLEEP: ERROR\r\n")
        elif buffer == "AT+IOTINFO\r\n":
            self.queue.append("+IOTINFO: IMSI=123123123 IMEI=123123123 Version=DUMMY\r\n")
        elif buffer.startswith("AT+IOTCGNSPWR="):
            if self.created:
                self.cgnpower = (buffer == "AT+IOTCGNSPWR=1\r\n")
                self.queue.append("+IOTCGNSPWR: SUCCESS\r\n")
            else:
                self.queue.append("+IOTCGNSPWR: ERROR\r\n")
        elif buffer == "AT+IOTCGNSINF\r\n":
            self.queue.append(
                "+IOTCGNSINF: ,1,20190729224430.000,50.7214446,-1.8805652,18.379,1.63,120.5,1,,3.3,3.5,1.0,,7,4,,,35,,\r\n")
        elif buffer.startswith("AT+IOTDEBUG="):
            self.queue.append("+IOTDEBUG: SUCCESS\r\n")
        elif buffer == "AT+IOTTEST\r\n":
            self.queue.append("AT+IOTTEST: SUCCESS\r\n")

    def deinit(self):
        pass
