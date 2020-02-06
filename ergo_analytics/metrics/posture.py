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


class PostureScore(BaseScore):
    """Computes a score based on time spent beyond given threshold angles.

    This is also known as teh posture score.
    """

    def _compute_single_window(self, angles=None, delta_time=None,
                               window_start=None, window_end=None,
                               percentile_middle=50, threshold_angle=45,
                               **kwargs):
        """Computes the posture for a single window."""

        angles = angles.copy().iloc[window_start:window_end]
        middle_val = percentile(angles, percentile_middle)

        angles -= middle_val

        # how much time was spent beyond the threshold:
        percent_beyond = \
            (angles[absolute(angles) > threshold_angle]).count() / len(angles) * 10
        # ^ note: we bring the posture on a scale from 0-10 here.

        return percent_beyond

    def _summarize_windows(self, values=None):
        """Computes the score from given values.

        So imagine that we compute a quantity like "% time spent beyond 40 deg".
        That quantity is collected per window. Finally, the values are passed here.
        Typically, we then bin them and compute the final score.
        """

        # now bin these in bins from 0 - 15 in steps of 1 (determined heuristically):
        bins = arange(11)  # (0, 1, 2, .., 10) --> posture is on that scale (see factor of 10 in _compute_single_window)
        m = len(bins) - 1
        values_binned_raw = compute_binned_score(bins=bins, values=values,
                                                 weighing_method='constant')

        posture_binned = normalize_to_scale(values_binned_raw,
                                            old_lo=0, old_hi=m,
                                            new_lo=0, new_hi=7)
        return float(posture_binned)

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
