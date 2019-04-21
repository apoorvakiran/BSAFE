# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["MultiServo"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from . import Servo


class MultiServo(Servo):
    """
    Can move multiple servos at once.
    """

    def __init__(self, list_of_pins=None):
        """
        Constructs a Multi Servo object.

        :param list_of_pins:
        """

        super().__init__(pin=list_of_pins)
