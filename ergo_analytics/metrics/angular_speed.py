# -*- coding: utf-8 -*-
"""
Computes the posture score among the Iterate Labs Ergo Metrics.

@ author Jesper Kristensen and Jacob Tyrrell
Copyright Iterate Labs 2018-
"""

__all__ = ["AngularSpeedScore"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import shutil
from numpy import absolute
from numpy import append
from numpy import arange
from numpy import clip
from numpy import gradient
from numpy import median
import matplotlib.pyplot as plt
from ergo_analytics.metrics import compute_binned_score
from ergo_analytics.metrics import normalize_to_scale
from ergo_analytics.metrics import BaseScore
import logging

logger = logging.getLogger()


class AngularSpeedScore(object):
    """Computes a score based on angular speed."""

    def __init__(self):
        pass

    def compute(self, delta_pitch=None, delta_yaw=None,
                delta_roll=None, method='binning', exclude_angles=None,
                debug=True, store_plots_here=None, prepend=None, **kwargs):
        """
        Computes the angular speed score. This is a score which captures the change-
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

        if debug and store_plots_here is None:
            store_plots_here = '~'

        store_plots_here = os.path.abspath(os.path.expanduser(store_plots_here))

        if os.path.isdir(store_plots_here):
            shutil.rmtree(store_plots_here)

        os.makedirs(store_plots_here)

        if len(delta_yaw) < 10:
            # do not compute gradients (not enough data) - so put nothing:
            std_yaw = 0
            std_pitch = 0
            std_roll = 0
            speed_scores = dict(yaw_raw=std_yaw, pitch_raw=std_pitch,
                                roll_raw=std_roll)
            return speed_scores

        if exclude_angles is None:
            exclude_angles = ()

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
            gradient_yaw = absolute(gradient_yaw)
            gradient_pitch = absolute(gradient_pitch)
            gradient_roll = absolute(gradient_roll)

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

            if 'yaw' in exclude_angles:
                speed_score_yaw_raw = 0
            if 'pitch' in exclude_angles:
                speed_score_pitch_raw = 0
            if 'roll' in exclude_angles:
                speed_score_roll_raw = 0

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

        elif method == 'rolling_window':

            # we move a window across the data of various widths.
            # The width in essence is time and the delta angle
            # across the window is just that.

            widths = [2, 3, 5, 10]
            speed_scores = []
            for width in widths:

                start = 0
                all_speeds = []
                for ix in range(len(delta_yaw)):

                    # this_window_start = int(start + (ix * width / 2))
                    this_window_start = int(start + (ix * width))
                    this_window_end = int(this_window_start + width)

                    if this_window_end >= len(delta_yaw):
                        break

                    delta_time = width  # by def.

                    max_angle = delta_yaw.iloc[this_window_start:this_window_end].max()
                    min_angle = delta_yaw.iloc[this_window_start:this_window_end].min()
                    delta_angle = absolute(max_angle - min_angle)

                    # start_angle = delta_yaw.iloc[this_window_start]
                    # end_angle = delta_yaw.iloc[this_window_end]
                    # delta_angle = end_angle - start_angle

                    this_speed = absolute(delta_angle / delta_time)  # deg/s
                    this_speed = clip(this_speed, a_min=None, a_max=180)

                    all_speeds.append(this_speed)

                if debug:

                    plt.figure()
                    plt.subplot(211)
                    plt.plot(all_speeds, 'b-')
                    plt.grid()
                    # plt.xlabel("Index")
                    plt.ylabel("|D_angle / D_time| (window={})".format(width))
                    plt.ylim(0, plt.gca().get_ylim()[1])

                    plt.subplot(212)
                    plt.plot(delta_yaw, 'r-')
                    plt.grid()
                    plt.xlabel("Index")
                    plt.ylabel("angle (window={})".format(width))

                    plt.tight_layout()

                    plt.savefig(os.path.join(store_plots_here, '{}_width_{}_angular_speed.png'.format(prepend,
                                                                                                      width)))
                    # plt.close()

                # now bin these in bins from 0 - 15 in steps of 1 (determined heuristically):
                bins = arange(11)
                bins = append(bins, [180])
                m = len(bins) - 1
                speed_score_yaw_raw = compute_binned_score(bins=bins,
                                                           values=all_speeds,
                                                           weighing_method='constant')

                speed_score_yaw = normalize_to_scale(speed_score_yaw_raw,
                                                     old_lo=0, old_hi=m, new_lo=0, new_hi=7)

                speed_scores.append(speed_score_yaw)

            if debug:
                plt.figure()
                plt.plot(widths, speed_scores, 'ro-', label='speed')
                plt.axhline(median(speed_scores), linestyle='--', color='k', label='median')
                plt.xlabel("window width")
                plt.ylabel("speed score")
                plt.grid()
                plt.ylim(0, 7)
                plt.legend(loc='best')

                plt.gca().fill_between(widths, 0, 3, alpha=0.2, facecolor='g')
                plt.gca().fill_between(widths, 3, 5, alpha=0.2, facecolor='y')
                plt.gca().fill_between(widths, 5, 7, alpha=0.2, facecolor='r')
                plt.savefig(os.path.join(store_plots_here, 'speed_vs_window.png'))

        else:
            raise NotImplementedError("Implement me!")

        return speed_scores
