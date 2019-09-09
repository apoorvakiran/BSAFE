# -*- coding: utf-8 -*-
"""
This code offers ways to interact with the arduino board as a Python object.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["ArduinoData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from .base_data import BaseData


class ArduinoData(BaseData):
    """
    Handles reading/writing data to and from Arduino boards.
    """

    def __init__(self):

        super().__init__()

        self._board = self._locate_arduino_port()

    @property
    def board(self):
        return self._board

    def _locate_arduino_port(self):

        from pyfirmata import ArduinoMega
        from serial.tools import list_ports

        board = None
        usb_port = None
        all_ports = list_ports.comports()
        all_usb_ports = []
        for port in all_ports:
            if port.device.split('cu.')[1].startswith('usb'):
                usb_port = port.device
                all_usb_ports.append(usb_port)

        if len(all_usb_ports) == 0:
            raise Exception("Looks like the Arduino is not plugged in!")

        for usb_port in all_usb_ports:
            try:
                print(f"Trying port {usb_port}...")
                board = ArduinoMega(usb_port)  # usb port
            except Exception as msg:
                print(" -- Error with this port")
                continue

        if board is None:
            raise Exception("The board was not found in any of the USB ports?")

        return board
