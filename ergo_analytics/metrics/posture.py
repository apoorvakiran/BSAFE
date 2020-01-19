# -*- coding: utf-8 -*-
"""Computes a score which aggregates time spent beyond given angular thresholds.

This is also called the Posture score.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
All Rights Reserved.
"""

__all__ = ["PostureScore"]
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
from numpy import max
from numpy import percentile
import matplotlib.pyplot as plt
from ergo_analytics.metrics import compute_binned_score
from ergo_analytics.metrics import normalize_to_scale
from ergo_analytics.metrics import BaseScore
import logging

logger = logging.getLogger()


class PostureScore(object):
    """Computes a score based on time spent beyond given threshold angles.

    This is also known as teh posture score.
    """

    def __init__(self):
        pass

    def _compute_posture_single_window(self, angles=None, delta_time=None,
                                       window_start=None, window_end=None,
                                       percentile_middle=50, threshold_angle=45):
        """Computes the posture for a single window."""

        middle_val = percentile(angles, percentile_middle)

        angles -= middle_val

        # how much time was spent beyond the threshold:
        percent_beyond = \
            (angles[absolute(angles) > threshold_angle]).count() / len(angles)

        return percent_beyond

    def compute(self, delta_pitch=None, delta_yaw=None,
                delta_roll=None, exclude_angles=None, debug=True,
                store_plots_here=None, prepend=None, percentile_middle=50,
                threshold_angle=45, widths=None, combine_scores='max',
                **kwargs):
        """Computes the Activity score. This is a score which captures the change-
        in angle vs. time. If this occurs faster the assumption is that there
        is an associated lower level of ergonomics.

        First, velocity is approximated as the gradient of the angle in time.
        We imagine this creating a distribution of instantenous values.
        When this distribution is wide it means that we see many
        high-valued velocities. So the wider / higher std dev the higher
        the score should be.

        This measures the width of the distribution of instantenous velocities.
        """

        if delta_pitch is None and delta_yaw is None and delta_roll is None:
            msg = "all incoming delta-angles are None!" \
                  "Returning just None for the score."
            logger.debug(msg)
            return None

        if debug:
            if store_plots_here is None:
                store_plots_here = '~'

            store_plots_here = os.path.abspath(os.path.expanduser(store_plots_here))
            if os.path.isdir(store_plots_here):
                shutil.rmtree(store_plots_here)

            os.makedirs(store_plots_here)

        if exclude_angles is None:
            exclude_angles = {}

        # we move a window across the data of various widths.
        # The width in essence is time and the delta angle
        # across the window is just that.

        if widths is None:
            widths = [2, 3, 4, 5, 6, 7, 8, 9, 10]

        percentile = 50  # where to assume the zero-level is
        all_posture_scores = []
        for widthix, width in enumerate(widths):

            start = 0
            all_postures_this_width = dict(yaw=[], pitch=[], roll=[])
            for ix in range(len(delta_yaw)):

                # this_window_start = int(start + (ix * width / 2))
                this_window_start = int(start + (ix * width))
                this_window_end = int(this_window_start + width)
                delta_time = width  # by def.

                if this_window_end >= len(delta_yaw):
                    break

                if 'yaw' not in exclude_angles:
                    ix_yaw_activity = self._compute_posture_single_window(
                        angles=delta_yaw,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end,
                        percentile_middle=percentile_middle,
                        threshold_angle=threshold_angle
                    )
                else:
                    ix_yaw_activity = 0

                if 'pitch' not in exclude_angles:
                    ix_pitch_activity = self._compute_posture_single_window(
                        angles=delta_pitch,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end,
                        percentile_middle=percentile_middle
                    )
                else:
                    ix_pitch_activity = 0

                if 'roll' not in exclude_angles:
                    ix_roll_activity = self._compute_posture_single_window(
                        angles=delta_roll,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end,
                        percentile_middle=percentile_middle,
                        threshold_angle=threshold_angle
                    )
                else:
                    ix_roll_activity = 0

                all_postures_this_width['yaw'].append(ix_yaw_activity)
                all_postures_this_width['pitch'].append(ix_pitch_activity)
                all_postures_this_width['roll'].append(ix_roll_activity)

            if debug:
                collected_angles = dict(yaw=delta_yaw, pitch=delta_pitch, roll=delta_roll)
                for angle_name in ('yaw', 'pitch', 'roll'):
                    if angle_name not in exclude_angles:

                        PostureScore._plot_scoring(angle_name=angle_name,
                                                   angles=collected_angles[angle_name],
                                                   width=width, prepend=f"width_{widthix}_{prepend}",
                                                   store_plots_here=store_plots_here,
                                                   all_postures_this_width=all_postures_this_width,
                                                   percentile_middle=percentile_middle,
                                                   threshold_angle=threshold_angle)

            yaw_score = self._compute_score(
                posture_values=all_postures_this_width['yaw'])
            pitch_score = self._compute_score(
                posture_values=all_postures_this_width['pitch'])
            roll_score = self._compute_score(
                posture_values=all_postures_this_width['roll'])

            if combine_scores == 'max':
                summarized_score = max([pitch_score, yaw_score, roll_score])
            elif combine_scores == 'keep-separate':
                summarized_score = (pitch_score, yaw_score, roll_score)
            else:
                raise NotImplementedError("Implement me!")

            all_posture_scores.append(summarized_score)

        # if debug:
        #     plt.figure()
        #     plt.plot(widths, all_posture_scores, 'ro-')
        #     plt.axhline(median(all_posture_scores), linestyle='--',
        #                 color='k', label='median')
        #     plt.xlabel("window width")
        #     plt.ylabel("posture score")
        #     plt.grid()
        #     plt.ylim(0, 7)
        #     plt.legend(loc='best')
        #
        #     plt.gca().fill_between(widths, 0, 3, alpha=0.2, facecolor='g')
        #     plt.gca().fill_between(widths, 3, 5, alpha=0.2, facecolor='y')
        #     plt.gca().fill_between(widths, 5, 7, alpha=0.2, facecolor='r')
        #     plt.savefig(os.path.join(store_plots_here, 'posture_vs_parameter.png'))

        return all_posture_scores, {"widths": widths}

    def _compute_score(self, posture_values=None):
        """Computes the score from given posture values."""

        # # now bin these in bins from 0 - 15 in steps of 1 (determined heuristically):
        # bins = arange(11)
        # m = len(bins) - 1
        #
        # activities_binned_raw = compute_binned_score(bins=bins,
        #                                              values=posture_values,
        #                                              weighing_method='constant')
        posture_binned = normalize_to_scale(posture_values,
                                            old_lo=0, old_hi=1,
                                            new_lo=0, new_hi=7)
        return posture_binned

    @staticmethod
    def _plot_scoring(angle_name=None, width=None, prepend=None,
                      store_plots_here=None, angles=None,
                      all_postures_this_width=None, percentile_middle=None,
                      threshold_angle=None, combine_scores=None):
        """Plots these scoring details for the given angle_name."""

        if combine_scores not in ('keep-separate', ):

            plt.figure()
            plt.subplot(211)
            plt.plot(all_postures_this_width[angle_name], 'b-')
            plt.grid()
            plt.ylabel(f"% time beyond {threshold_angle} (width={width})")
            plt.ylim(0, 1)

            plt.subplot(212)
            plt.plot(angles - percentile(angles, percentile_middle), 'r-', label='angles')
            plt.plot(absolute(angles - percentile(angles, percentile_middle)), 'g--', label='abs(angles)')
            plt.axhline(threshold_angle, linestyle='--', label='threshold')
            plt.legend(loc='best')
            plt.grid()
            plt.xlabel("Index")
            plt.ylabel("{} angle (width={})".format(angle_name, width))
            plt.tight_layout()
            plt.savefig(os.path.join(store_plots_here,
                                     '{}_width_{}_posture_{}.png'.format(prepend,
                                                                          width,
                                                                          angle_name)))
