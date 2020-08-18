# -*- coding: utf-8 -*-
"""Interface of an ErgoMetric score.

@ author Jesper Kristensen
Copyright Iterate Labs Inc.
All Rights Reserved.
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

__all__ = ["BaseScore"]

import os
import logging

logger = logging.getLogger()


class BaseScore(object):
    def __init__(self):
        pass

    def compute(
        self,
        delta_pitch=None,
        delta_yaw=None,
        delta_roll=None,
        exclude_angles=None,
        debug=True,
        store_plots_here=None,
        prepend=None,
        widths=None,
        **kwargs,
    ):
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
            msg = (
                "all incoming delta-angles are None!"
                "Returning just None for the score."
            )
            logger.debug(msg)
            return None

        if debug:
            if store_plots_here is None:
                store_plots_here = "~"

            store_plots_here = os.path.abspath(os.path.expanduser(store_plots_here))
            if os.path.isdir(store_plots_here):
                shutil.rmtree(store_plots_here)

            os.makedirs(store_plots_here)

        if exclude_angles is None:
            exclude_angles = {}

        # we move a window across the data of various widths.
        # The width in essence is time and the delta angle
        # across the window is just that.

        if widths is None or len(widths) == 0:
            widths = [2, 3, 4, 5, 6, 7, 8, 9, 10]

        all_activity_scores = dict()
        for widthix, width in enumerate(widths):

            start = 0
            all_activities_this_width = dict(yaw=[], pitch=[], roll=[])
            for ix in range(len(delta_yaw)):

                # this_window_start = int(start + (ix * width / 2))
                this_window_start = int(start + (ix * width))
                this_window_end = int(this_window_start + width)
                delta_time = width  # by def.

                if this_window_end >= len(delta_yaw):
                    break

                if "yaw" not in exclude_angles:
                    ix_yaw_activity = self._compute_single_window(
                        angles=delta_yaw,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end,
                        **kwargs,
                    )
                else:
                    ix_yaw_activity = 0

                if "pitch" not in exclude_angles:
                    ix_pitch_activity = self._compute_single_window(
                        angles=delta_pitch,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end,
                        **kwargs,
                    )
                else:
                    ix_pitch_activity = 0

                if "roll" not in exclude_angles:
                    ix_roll_activity = self._compute_single_window(
                        angles=delta_roll,
                        delta_time=delta_time,
                        window_start=this_window_start,
                        window_end=this_window_end,
                        **kwargs,
                    )
                else:
                    ix_roll_activity = 0

                all_activities_this_width["yaw"].append(ix_yaw_activity)
                all_activities_this_width["pitch"].append(ix_pitch_activity)
                all_activities_this_width["roll"].append(ix_roll_activity)

            if debug:
                collected_angles = dict(
                    yaw=delta_yaw, pitch=delta_pitch, roll=delta_roll
                )
                for angle_name in ("yaw", "pitch", "roll"):
                    if angle_name not in exclude_angles:
                        AngularActivityScore._plot_scoring(
                            angle_name=angle_name,
                            angles=collected_angles[angle_name],
                            width=width,
                            prepend=f"width_{widthix}_{prepend}",
                            store_plots_here=store_plots_here,
                            all_activities_this_width=all_activities_this_width,
                        )

            yaw_score = self._summarize_windows(values=all_activities_this_width["yaw"])
            pitch_score = self._summarize_windows(
                values=all_activities_this_width["pitch"]
            )
            roll_score = self._summarize_windows(
                values=all_activities_this_width["roll"]
            )

            all_activity_scores[width] = [yaw_score, pitch_score, roll_score]

        # if debug:
        #     plt.figure()
        #     plt.plot(widths, all_activity_scores, 'ro-')
        #     plt.axhline(median(all_activity_scores), linestyle='--',
        #                 color='k', label='median')
        #     plt.xlabel("window width")
        #     plt.ylabel("activity score")
        #     plt.grid()
        #     plt.ylim(0, 7)
        #     plt.legend(loc='best')
        #
        #     plt.gca().fill_between(widths, 0, 3, alpha=0.2, facecolor='g')
        #     plt.gca().fill_between(widths, 3, 5, alpha=0.2, facecolor='y')
        #     plt.gca().fill_between(widths, 5, 7, alpha=0.2, facecolor='r')
        #     plt.savefig(os.path.join(store_plots_here, 'activity_vs_parameter.png'))

        return all_activity_scores
