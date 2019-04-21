# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["validate_angle"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

# constants
MS_PER_SECOND = 1000


def validate_angle(angle=None):
    """
    Validates an incoming angle.

    :param angle: float or int representing the angle.
    :return: True if valid, raises Exception if not.
    """

    if angle is None:
        raise Exception("Please input an angle that is not None!")

    try:
        angle = float(angle)
    except Exception:
        raise Exception("Was unable to cast incoming angle {} to a numeric!".format(angle))

    if 0 > angle > 255:
        raise Exception("Angle {} is outside the valid range of (0, 255)!".format(angle))

    return True
