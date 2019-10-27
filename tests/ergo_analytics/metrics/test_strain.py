# -*- coding: utf-8 -*-
"""
Tests the implementation of the strain score.

@ author Jesper Kristensen
Copyright Iterate Labs, Inc. 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import pytest
from ergo_analytics.metrics import _custom_weighted_sum
from ergo_analytics.metrics import compute_strain_score


def test_strain_constant_weights():
    """
    Run a test to confirm that the strain score makes sense.
    """

    # lowest case: all time spent in 0-15 degrees
    list_of_bins = [400, 0, 0, 0, 0]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    # with constant weighing method, we assign equal weight of 1/num_bins
    # to each bin - so score is 1/num_bins = 1/5 = 0.2:
    assert score == 0

    # highest case:
    list_of_bins = [0, 0, 0, 0, 400]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    assert score == 4  # same score as above, since we are not ramping up
    # assigning more score to higher values

    list_of_bins = [0.5, 0, 0, 0, 0.5]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    assert score == 2  # half of 0 + half of 4 = 2

    list_of_bins = [0, 0.5, 0, 0, 0.5]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    assert score == 2.5  # half of 1 + half of 4 = 2.5

    list_of_bins = [0, 0.5, 0, 0, 0, 0.5]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='constant')
    # ^^ note: this function returns the score on the scale [0, m] where
    # m is the number of bins (now 5 instead of 4 in the above tests):
    assert score == 3  # half of 1 + half of 5 = 3

    delta_yaw = [0, 0, 0, 0, 0]
    delta_pitch = [0, 0, 0, 0, 0]
    delta_roll = [0, 0, 0, 0, 0]
    strain_score = compute_strain_score(delta_yaw=delta_yaw,
                                        delta_pitch=delta_pitch,
                                        delta_roll=delta_roll,
                                        normalize_to_scale=(0, 7),
                                        weighing_method='linear')

    assert strain_score == {'yaw_raw': 0, 'pitch_raw': 0, 'roll_raw': 0,
                            'yaw': 0, 'pitch': 0, 'roll': 0,
                            'total': 0}

    delta_yaw = [0, 16, 0, 0, 21]  # 2 counts in bin 2 (15-29)
    delta_pitch = [0, 0, 28, 0, 0]
    delta_roll = [0, 0, 0, 0, 20]
    strain_score = compute_strain_score(delta_yaw=delta_yaw,
                                        delta_pitch=delta_pitch,
                                        delta_roll=delta_roll,
                                        normalize_to_scale=(0, 7),
                                        weighing_method='linear')

    assert strain_score == {'yaw_raw': 0.3636363636363637,
                            'pitch_raw': 0.2121212121212121,
                            'roll_raw': 0.2121212121212121,
                            'yaw': 0.3636363636363637,
                            'pitch': 0.2121212121212121,
                            'roll': 0.2121212121212121,
                            'total': 0.2626262626262626}

    delta_yaw = [0, 178, 0, 0, 21]  # 2 counts in bin 2 (15-29)
    delta_pitch = [0, 0, 28, 0, 0]
    delta_roll = [0, 0, 0, 0, 20]
    strain_score = compute_strain_score(delta_yaw=delta_yaw,
                                        delta_pitch=delta_pitch,
                                        delta_roll=delta_roll,
                                        normalize_to_scale=(0, 7),
                                        weighing_method='linear')

    # now yaw should be higher than the others
    assert strain_score == {'yaw_raw': 5.016042780748664,
                            'pitch_raw': 0.2121212121212121,
                            'roll_raw': 0.2121212121212121,
                            'yaw': 5.016042780748664,
                            'pitch': 0.2121212121212121,
                            'roll': 0.2121212121212121,
                            'total': 1.813428401663696}

    delta_yaw = [180, 180, 180, 180, 1]  # 2 counts in bin 2 (15-29)
    delta_pitch = [0, 0, 28, 0, 0]
    delta_roll = [0, 0, 0, 0, 20]
    strain_score = compute_strain_score(delta_yaw=delta_yaw,
                                        delta_pitch=delta_pitch,
                                        delta_roll=delta_roll,
                                        normalize_to_scale=(0, 7),
                                        weighing_method='linear')

    assert strain_score == {'yaw_raw': 6.857142857142858,
                            'pitch_raw': 0.2121212121212121,
                            'roll_raw': 0.2121212121212121,
                            'yaw': 6.857142857142858,
                            'pitch': 0.2121212121212121,
                            'roll': 0.2121212121212121,
                            'total': 2.427128427128427}

    # now add in more time points with low risk:
    delta_yaw = [180, 180, 180, 180, 0, 0, 0, 0, 0, 0]
    delta_pitch = [0, 0, 28, 0, 0]
    delta_roll = [0, 0, 0, 0, 20]
    strain_score = compute_strain_score(delta_yaw=delta_yaw,
                                        delta_pitch=delta_pitch,
                                        delta_roll=delta_roll,
                                        normalize_to_scale=(0, 7),
                                        weighing_method='linear')

    assert strain_score == {'yaw_raw': 6.222222222222222,
                            'pitch_raw': 0.2121212121212121,
                            'roll_raw': 0.2121212121212121,
                            'yaw': 6.222222222222222,
                            'pitch': 0.2121212121212121,
                            'roll': 0.2121212121212121,
                            'total': 2.2154882154882154}

    delta_yaw = [180, 180, 180, 180, 0, 0, 0, 0, 0, 0]
    delta_yaw += [0] * 1000  # add a lot of time where we are not high risk
    delta_pitch = [0, 0, 28, 0, 0]
    delta_roll = [0, 0, 0, 0, 20]
    strain_score = compute_strain_score(delta_yaw=delta_yaw,
                                        delta_pitch=delta_pitch,
                                        delta_roll=delta_roll,
                                        normalize_to_scale=(0, 7),
                                        weighing_method='linear')

    assert strain_score == {'yaw_raw': 0.3187855787476281,
                            'pitch_raw': 0.2121212121212121,
                            'roll_raw': 0.2121212121212121,
                            'yaw': 0.3187855787476281,
                            'pitch': 0.2121212121212121,
                            'roll': 0.2121212121212121,
                            'total': 0.24767600099668408}

    # very aggressive:
    delta_yaw = [0, 140, 140, 0, 170]  # 2 counts in bin 2 (15-29)
    delta_pitch = [0, 0, 180, 0, 0]
    delta_roll = [0, 0, 0, 0, 180]
    strain_score = compute_strain_score(delta_yaw=delta_yaw,
                                        delta_pitch=delta_pitch,
                                        delta_roll=delta_roll,
                                        normalize_to_scale=(0, 7),
                                        weighing_method='linear')

    assert strain_score == {'yaw_raw': 5.839572192513368,
                            'pitch_raw': 5.250000000000001,
                            'roll_raw': 5.250000000000001,
                            'yaw': 5.839572192513368,
                            'pitch': 5.250000000000001,
                            'roll': 5.250000000000001,
                            'total': 5.446524064171123}

def test_strain_linear_weights():

    list_of_bins = [0, 0, 0, 0, 0.5]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='linear')
    assert score == 4

    list_of_bins = [0, 0.5, 0, 0, 0.5]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='linear')
    assert score == pytest.approx(3.1428, 0.0001)


def test_strain_quadratic_weights():

    list_of_bins = [0, 0, 0, 0, 0.5]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='quadratic')
    assert score == 4

    list_of_bins = [0, 0.5, 0, 0, 0.5]
    score = _custom_weighted_sum(list_of_bins=list_of_bins,
                                 weighing_method='quadratic')
    assert score == pytest.approx(3.586206, 0.0001)
