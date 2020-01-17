# -*- coding: utf-8 -*-
"""Computes the Angular Activity score among the Iterate Labs Ergo Metrics.

This measures, in a summarized fashion, the range of angles visited in a given
time interval. The idea being that, the larger the difference between extreme
values of the angle, the more active and hence prone to injury.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
"""

__all__ = ["AngularActivityScore"]
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
import matplotlib.pyplot as plt
from ergo_analytics.metrics import compute_binned_score
from ergo_analytics.metrics import normalize_to_scale
from ergo_analytics.metrics import BaseScore
import logging

logger = logging.getLogger()


class AngularActivityScore(object):
    """Computes a score based on activity - range of angles."""

    def __init__(self):
        pass

    def _compute_activity_single_window(self, angles=None, delta_time=None,
                                        window_start=None, window_end=None):
        """Computes the activity for a single window."""

        max_angle = angles.iloc[window_start:window_end].max()
        min_angle = angles.iloc[window_start:window_end].min()
        delta_angle = absolute(max_angle - min_angle)

        # start_angle = delta_yaw.iloc[this_window_start]
        # end_angle = delta_yaw.iloc[this_window_end]
        # delta_angle = end_angle - start_angle

        this_activity = absolute(delta_angle / delta_time)
        this_activity = clip(this_activity, a_min=None, a_max=180)

        return this_activity

    def compute(self, delta_pitch=None, delta_yaw=None,
                delta_roll=None, exclude_angles=None, debug=True,
                store_plots_here=None, prepend=None, **kwargs):
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

        widths = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        all_activity_scores = []
        for width in widths:

            start = 0
            all_activities_this_width = dict(yaw=[], pitch=[], roll=[])
            for ix in range(len(delta_yaw)):

                # this_window_start = int(start + (ix * width / 2))
                this_window_start = int(start + (ix * width))
                this_window_end = int(this_window_start + width)
                delta_time = width  # by def.

                if this_window_end >= len(delta_yaw):
                    break

                if 'yaw' not in exclude_angles:
                    ix_yaw_activity = self._compute_activity_single_window(
                        angles=delta_yaw,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end
                    )
                else:
                    ix_yaw_activity = 0

                if 'pitch' not in exclude_angles:
                    ix_pitch_activity = self._compute_activity_single_window(
                        angles=delta_pitch,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end
                    )
                else:
                    ix_pitch_activity = 0

                if 'roll' not in exclude_angles:
                    ix_roll_activity = self._compute_activity_single_window(
                        angles=delta_roll,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end
                    )
                else:
                    ix_roll_activity = 0

                all_activities_this_width['yaw'].append(ix_yaw_activity)
                all_activities_this_width['pitch'].append(ix_pitch_activity)
                all_activities_this_width['roll'].append(ix_roll_activity)

            if debug:
                collected_angles = dict(yaw=delta_yaw, pitch=delta_pitch, roll=delta_roll)
                for angle_name in ('yaw', 'pitch', 'roll'):
                    if angle_name not in exclude_angles:

                        AngularActivityScore._plot_scoring(angle_name=angle_name,
                                                           angles=collected_angles[angle_name],
                                                           width=width, prepend=prepend,
                                                           store_plots_here=store_plots_here,
                                            all_activities_this_width=all_activities_this_width)

            yaw_score = self._compute_score(
                activity_values=all_activities_this_width['yaw'])
            pitch_score = self._compute_score(
                activity_values=all_activities_this_width['pitch'])
            roll_score = self._compute_score(
                activity_values=all_activities_this_width['roll'])

            max_score = max([pitch_score, yaw_score, roll_score])
            all_activity_scores.append(max_score)

        if debug:
            plt.figure()
            plt.plot(widths, all_activity_scores, 'ro-')
            plt.axhline(median(all_activity_scores), linestyle='--',
                        color='k', label='median')
            plt.xlabel("window width")
            plt.ylabel("activity score")
            plt.grid()
            plt.ylim(0, 7)
            plt.legend(loc='best')

            plt.gca().fill_between(widths, 0, 3, alpha=0.2, facecolor='g')
            plt.gca().fill_between(widths, 3, 5, alpha=0.2, facecolor='y')
            plt.gca().fill_between(widths, 5, 7, alpha=0.2, facecolor='r')
            plt.savefig(os.path.join(store_plots_here, 'activity_vs_parameter.png'))

        return all_activity_scores

    def _compute_score(self, activity_values=None):
        """Computes the score from given activity values."""

        # now bin these in bins from 0 - 15 in steps of 1 (determined heuristically):
        bins = arange(11)
        bins = append(bins, [180])
        m = len(bins) - 1

        activities_binned_raw = compute_binned_score(bins=bins,
                                                     values=activity_values,
                                                     weighing_method='constant')
        activities_binned = normalize_to_scale(activities_binned_raw,
                                               old_lo=0, old_hi=m,
                                               new_lo=0, new_hi=7)
        return activities_binned

    @staticmethod
    def _plot_scoring(angle_name=None, width=None, prepend=None,
                      store_plots_here=None, angles=None,
                      all_activities_this_width=None):
        """Plots these scoring details for the given angle_name."""

        plt.figure()
        plt.subplot(211)
        plt.plot(all_activities_this_width[angle_name], 'b-')
        plt.grid()
        plt.ylabel("|max-min|/Dt (width={})".format(
            angle_name, angle_name, width))
        plt.ylim(0, plt.gca().get_ylim()[1])

        plt.subplot(212)
        plt.plot(angles, 'r-')
        plt.grid()
        plt.xlabel("Index")
        plt.ylabel("{} angle (width={})".format(angle_name, width))
        plt.tight_layout()
        plt.savefig(os.path.join(store_plots_here,
                                 '{}_width_{}_activity_{}.png'.format(prepend,
                                                                      width,
                                                                      angle_name)))
