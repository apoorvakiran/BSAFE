# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["BaseServo"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
from Analytics.RawData import ArduinoData


class BaseServo(object):
    """
    Code for being a Base Servo.
    """

    _board_pins = None

    def __init__(self, pins=None):
        """
        Constructs a base servo object.

        :param servo:
        """
        try:
            pins = list(np.atleast_1d(pins))
        except Exception:
            raise Exception("Please input a valid argument for 'pins', should be a list of strings like ['8', 12']\n"
                            "but can also be a single string like '21'.")

        servos = BaseServo.create_pins(list_of_pins=pins)
        self._board_pins = dict()
        for pin, servo in zip(pins, servos):
            self._board_pins[pin] = servo

    @staticmethod
    def create_pins(list_of_pins=None):
        """
        Creates servo objects based on incoming list of pins (strings).

        :param list_of_pins: ['8', '12'] if the digital pins 8 and 12 are connected to servos.
        :type list_of_pins: list of str
        :return:
        """
        if list_of_pins is None or len(list_of_pins) == 0:
            raise Exception("There was an issue with the incoming list of pins!")

        data = ArduinoData()  # connects you to the board
        board = data.board
        board_pins = []
        for pin_number in list_of_pins:
            print("Creating servo for pin {}...".format(pin_number))
            try:
                board_pins.append(board.get_pin('d:{}:s'.format(str(int(pin_number)))))
            except Exception as msg:
                print(msg)
                raise Exception("There was an issue creating the Servo object for pin {}".format(pin_number))

        return board_pins
