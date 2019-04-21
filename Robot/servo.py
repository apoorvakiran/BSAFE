# -*- coding: utf-8 -*-
"""
Contains libraries to manipulate Servos.

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["Servo"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import time as time_c
import numpy as np
from . import BaseServo
from .utilities import MS_PER_SECOND, validate_angle


class Servo(BaseServo):
    """
    Defines a Servo object representing a physical Servo on the Robot arm.
    """

    def __init__(self, pin=None):
        """
        Constructs a servo.

        :param pin:
        """
        super().__init__(pins=pin)

    def sweep(self, ranges=None, periods_seconds=None, sleep_time_ms=100):
        """
        Sweeps the robot arm by first starting at the "start" angle.
        Then sweeps from range[0] to range[1].

        :param range: tuple of 2 elements: First element is the angle to sweep from (in degrees),
        second element is angle to sweep to in degrees.
        :return: None
        """

        servo_lib = dict()
        if len(ranges) == 2 and len(self._board_pins) > len(ranges):
            ranges = [ranges] * len(self._board_pins)

        if len(ranges) == 2 and len(self._board_pins) == 1:
            ranges = [ranges]

        periods_seconds = list(np.atleast_1d(periods_seconds))

        pin = [None] * len(self._board_pins)
        deg_per_sleep = [None] * len(self._board_pins)
        deg_per_s = [None] * len(self._board_pins)
        minVal = [None] * len(self._board_pins)
        maxVal = [None] * len(self._board_pins)
        val = [None] * len(self._board_pins)
        sign = [None] * len(self._board_pins)
        period_seconds = [None] * len(self._board_pins)

        for ix, (range_single_servo, period, this_pin) in enumerate(zip(ranges, periods_seconds, self._board_pins)):
            # for each servo...

            assert len(range_single_servo) == 2
            assert isinstance(range_single_servo[0], (int, float))
            assert isinstance(range_single_servo[1], (int, float))
            assert range_single_servo[1] >= range_single_servo[0]

            if range_single_servo[1] == range_single_servo[0]:
                print("The range start point equals the end point - returning...")
                return

            sign[ix] = 1
            val[ix] = range_single_servo[0]
            minVal[ix] = range_single_servo[0]
            maxVal[ix] = range_single_servo[1]
            pin[ix] = self._board_pins[this_pin]
            period_seconds[ix] = period
            deg_per_s[ix] = (maxVal[ix] - minVal[ix]) * (1 / period_seconds[ix])  # turn in chunks of (1/T)
            deg_per_sleep[ix] = deg_per_s[ix] * (sleep_time_ms / MS_PER_SECOND)

        sign = np.asarray(sign).astype(float)
        val = np.asarray(val).astype(float)
        minVal = np.asarray(minVal).astype(float)
        maxVal = np.asarray(maxVal).astype(float)
        pin = np.asarray(pin)
        period_seconds = np.asarray(period_seconds).astype(float)
        deg_per_s = np.asarray(deg_per_s).astype(float)
        deg_per_sleep = np.asarray(deg_per_sleep).astype(float)

        start_c = time_c.time()

        while True:
            # Keep moving the servo back and forth

            # validate_angle(val)
            list(map(lambda this_pin, this_value: this_pin.write(float(this_value)), pin, val))

            val += sign * deg_per_sleep

            max_exceed_ix = np.where(val >= maxVal)[0]
            sign[max_exceed_ix] = -1

            min_exceed_ix = np.where(val <= minVal)[0]
            sign[min_exceed_ix] = 1

            time_c.sleep(sleep_time_ms / MS_PER_SECOND)

            # check the time (make sure it matches the period):
            print('current time = {:.1f} s.'.format(time_c.time() - start_c))

    def move_to(self, value=None):
        """
        Moves servo to specific value.

        :param value:
        :return:
        """
        board_pins = self._board_pins
        validate_angle(value)
        for board_pin in board_pins:
            board_pin.write(float(value))
