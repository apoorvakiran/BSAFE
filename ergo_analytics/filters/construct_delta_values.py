# -*- coding: utf-8 -*-
"""
This transformation takes in data with yaw, pitch, and roll and
transforms this data into delta values. The delta refers to
values between the hand and wrist.

@ author Iterate Labs, Inc.
Copyright 2018-
"""

from scipy.spatial.transform import Rotation
import numpy as np

from . import BaseTransformation
import logging

__all__ = ["ConstructDeltaValues"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class ConstructDeltaValues(BaseTransformation):
    """
    Find the window of relevant data. For example, say the worker was not
    wearing the device for a while in the beginning or was setting up
    getting ready to start. Towards the end, maybe they did not turn off
    the device immediately.
    """

    def __init__(self):
        """
        Construct the standard deviation filter.
        """
        super().__init__()

    def _initialize_params(self):
        super()._initialize_params()

    def apply(self, data=None, **kwargs):
        """
        Leverage standard deviation to find where the data starts and ends.

        If the worker is not using the device and/or not working the standard
        deviation should be smaller than if working.

        :param data: data for which delta angles are to be constructed.
        :param data_format_code: which format is the data in?
        """
        super().apply(data=data, **kwargs)

        params = self._params
        if params['data_format_code'] in {'1', '2', '5'}:
            # construct delta angles between the two boards;
            # leverage rotation matrices to account for the two different
            # co-ordinate systems:
            wrist_board = Rotation.from_euler('ZYX',
                                data[['Yaw[0](deg)', 'Pitch[0](deg)',
                                      'Roll[0](deg)']].values * np.pi / 180)
            hand_board = Rotation.from_euler('ZYX',
                                             data[['Yaw[1](deg)', 'Pitch[1](deg)',
                                                   'Roll[1](deg)']].values * np.pi / 180)
            wrist_board_mat = wrist_board.as_matrix()
            hand_board_mat = hand_board.as_matrix()

            delta_angles = []
            for wrist_board_mat_tmp, hand_board_mat_tmp in \
                    zip(wrist_board_mat, hand_board_mat):
                delta_angle_tmp_mat = np.dot(wrist_board_mat_tmp,
                                             hand_board_mat_tmp.T)
                # for each point, construct the delta angles:
                delta_angle_tmp = Rotation.from_matrix(delta_angle_tmp_mat).as_euler('ZYX') * 180 / np.pi
                delta_angles.append(delta_angle_tmp)

            delta_angles = np.asarray(delta_angles)

            data.loc[:, 'DeltaYaw'] = delta_angles[:, 0]
            data.loc[:, 'DeltaPitch'] = delta_angles[:, 1]
            data.loc[:, 'DeltaRoll'] = delta_angles[:, 2]

        elif params['data_format_code'] == '4':
            # already in delta-angle format
            pass
        else:
            raise Exception("Implement me!")

        data_to_return = self._update_data(data_transformed=data,
                                           columns_operated_on=['DeltaYaw',
                                                                'DeltaPitch',
                                                                'DeltaRoll'])

        return data_to_return, \
               {'added': ['DeltaYaw', 'DeltaPitch', 'DeltaRoll']}
