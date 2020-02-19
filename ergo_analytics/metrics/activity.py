# -*- coding: utf-8 -*-
"""Computes the Angular Activity score among the Iterate Labs Ergo Metrics.

This measures, in a summarized fashion, the range of angles visited in a given
time interval. The idea being that, the larger the difference between extreme
values of the angle, the more active and hence prone to injury.

Note: This score may also be referred to, somewhat approximately, as the
speed score for historical reasons.

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
from numpy import array
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


class AngularActivityScore(BaseScore):
    """Computes a score based on activity - range of angles."""

    def _compute_single_window(self, angles=None, delta_time=None,
                               window_start=None, window_end=None, **kwargs):
        """Computes the activity for a single window."""

        angles = angles.copy().iloc[window_start:window_end]

        max_angle = angles.max()
        min_angle = angles.min()
        delta_angle = absolute(max_angle - min_angle)

        # start_angle = delta_yaw.iloc[this_window_start]
        # end_angle = delta_yaw.iloc[this_window_end]
        # delta_angle = end_angle - start_angle

        this_activity = absolute(delta_angle / delta_time)
        this_activity = clip(this_activity, a_min=None, a_max=180)

        return this_activity

    def _summarize_windows(self, values=None):
        """Computes the score from given activity values."""

        # now bin these in bins from 0 - 10 in steps of 1 (determined heuristically):
        bins = arange(11)
        bins = append(bins, [180])
        m = len(bins) - 1

        activities_binned_raw = compute_binned_score(bins=bins,
                                                     values=values,
                                                     weighing_method='constant')
        activities_binned = normalize_to_scale(activities_binned_raw,
                                               old_lo=0, old_hi=m,
                                               new_lo=0, new_hi=7)
        return float(activities_binned)

    @staticmethod
    def _plot_scoring(angle_name=None, width=None, prepend=None,
                      store_plots_here=None, angles=None,
                      all_activities_this_width=None, combine_scores=None):
        """Plots these scoring details for the given angle_name."""

        if combine_scores not in ('keep-separate', ):

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
