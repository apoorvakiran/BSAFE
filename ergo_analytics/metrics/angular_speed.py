# -*- coding: utf-8 -*-
"""
Computes the posture score among the Iterate Labs Ergo Metrics.

@ author Jesper Kristensen and Jacob Tyrrell
Copyright Iterate Labs 2018-
"""

__all__ = ["compute_angular_speed_score"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

from numpy import gradient
from numpy import absolute
from numpy import clip
from ergo_analytics.metrics import compute_binned_score
from ergo_analytics.metrics import normalize_to_scale
import logging

logger = logging.getLogger()


def compute_angular_speed_score(delta_pitch=None, delta_yaw=None,
                                delta_roll=None, method='binning', **kwargs):
    """
    Computes the angular speed score. This is a score which captures the change
    in angle vs. time. If this occurs faster the assumption is that there
    is an associated lower level of ergonomics.

    First, velocity is approximated as the gradient of the angle in time.
    We imagine this creating a distribution of instantenous values.
    When this distribution is wide it means that we see many
    high-valued velocities. So the wider / higher std dev the higher
    the score should be.

    This measures the width of the distribution of instantenous velocities.
    """

    if delta_pitch is None or delta_yaw is None or delta_roll is None:
        msg = "one or more of the incoming delta-angles is None!" \
              "Returning just None for the score."
        logger.debug(msg)
        return None

    if len(delta_yaw) < 10:
        # do not compute gradients (not enough data) - so put nothing:
        std_yaw = 0
        std_pitch = 0
        std_roll = 0
        speed_scores = dict(yaw_raw=std_yaw, pitch_raw=std_pitch,
                            roll_raw=std_roll)
        return speed_scores

    gradient_yaw = gradient(delta_yaw)
    gradient_pitch = gradient(delta_pitch)
    gradient_roll = gradient(delta_roll)

    # rough threshold: worker cannot change relative angle of hand/wrist
    # by more than 1/100th deg per second - just an assumption and helps
    # smooth the data:
    THRESHOLD_GRAD = 100  # discard data beyond this value

    if method == 'distribution':

        # get the width of the distribution:
        std_yaw = gradient_yaw[absolute(gradient_yaw) < THRESHOLD_GRAD].std()
        std_pitch = \
            gradient_pitch[absolute(gradient_pitch) < THRESHOLD_GRAD].std()
        std_roll = gradient_roll[absolute(gradient_roll) < THRESHOLD_GRAD].std()

        # TODO(JTK): To get these scores on a scale of 0-1 we need the datasets
        # TODO: collected representing "mild" "mid" and "severe".
        # TODO: Right now the score is somewhat "floating" around.
        # TODO: We may also need to condense the statistics of the
        # TODO: distribution in a different way (maybe more granular than just std)

        # summarize speed scores
        speed_scores = dict(yaw_raw=std_yaw, pitch_raw=std_pitch,
                            roll_raw=std_roll)

        speed_scores['yaw'] = speed_scores['yaw_raw'] * 7
        speed_scores['pitch'] = speed_scores['pitch_raw'] * 7
        speed_scores['roll'] = speed_scores['roll_raw'] * 7

    elif method == 'binning':

        # the bins need to be decided from calibration data:
        gradient_yaw = clip(gradient_yaw, a_min=None, a_max=THRESHOLD_GRAD)
        gradient_pitch = clip(gradient_pitch, a_min=None, a_max=THRESHOLD_GRAD)
        gradient_roll = clip(gradient_roll, a_min=None, a_max=THRESHOLD_GRAD)

        bins = [0.5, 1, 5, 10, THRESHOLD_GRAD]
        m = len(bins) - 1
        speed_score_yaw_raw = compute_binned_score(bins=bins,
                                                   values=gradient_yaw,
                                                   weighing_method='linear')
        speed_score_pitch_raw = compute_binned_score(bins=bins,
                                                     values=gradient_pitch,
                                                     weighing_method='linear')
        speed_score_roll_raw = compute_binned_score(bins=bins,
                                                    values=gradient_roll,
                                                    weighing_method='linear')

        # summarize speed scores
        speed_scores = dict(yaw_raw=speed_score_yaw_raw,
                            pitch_raw=speed_score_pitch_raw,
                            roll_raw=speed_score_roll_raw)

        speed_score_yaw = normalize_to_scale(speed_score_yaw_raw, old_lo=0,
                                             old_hi=m, new_lo=0, new_hi=7)
        speed_score_pitch = normalize_to_scale(speed_score_pitch_raw, old_lo=0,
                                               old_hi=m, new_lo=0, new_hi=7)
        speed_score_roll = normalize_to_scale(speed_score_roll_raw, old_lo=0,
                                              old_hi=m, new_lo=0, new_hi=7)

        speed_scores['yaw'] = speed_score_yaw
        speed_scores['pitch'] = speed_score_pitch
        speed_scores['roll'] = speed_score_roll

    else:
        raise NotImplementedError("Implement me!")

    return speed_scores
