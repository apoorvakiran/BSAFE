# -*- coding: utf-8 -*-
"""
Computes metrics for analyzing the data.

@ author Jesper Kristensen
Copyright 2018
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

__all__ = ["Metrics"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"


class Metrics(object):

    _experiments = None

    def __init__(self, experiments=None):

        self._experiments = experiments

    def compute_angular_velocity_score(self, task=None, motion_type=None, hand='right'):

        experiments = self._experiments

        _, yaw_data_segment1 = experiments.collect(type=motion_type, delta_sensors=True, hand=hand,
                                                   segment='1', task_name=task)
        _, yaw_data_segment2 = experiments.collect(type=motion_type, delta_sensors=True, hand=hand,
                                                   segment='2', task_name=task)

        def map_name(name):
            return name

        def compute_metric(omega=None):

            bins = np.arange(-210, 225, 15, dtype=float)

            bins[0] = -np.inf
            bins[-1] = np.inf

            total_value = 0
            for i in range(1, len(bins)):

                bin_start = bins[i - 1]
                bin_end = bins[i]

                if np.isinf(bin_start) or np.isinf(bin_end):
                    weight = min(np.abs(bin_start), np.abs(bin_end))

                else:
                    weight = max(np.abs(bin_start), np.abs(bin_end))

                omega_here = omega[(omega['omega'] > bin_start) &
                                   (omega['omega'] < bin_end)]
                omega_here = omega_here['omega'].abs()

                if len(omega_here) == 0:
                    continue

                weight = weight // 15  # add one for each 15 degree increment

                omega_here *= weight

                this_value = len(omega_here) / len(omega_here)

                total_value += this_value

            std = np.std(omega['omega'])

            return total_value, std

        metric_per_worker = {task: {}}

        plt.figure()
        for data_this_worker1, data_this_worker2 in zip(yaw_data_segment1, yaw_data_segment2):
            # for each worker...

            plt.subplot(211)
            time_delta = data_this_worker1.time_delta
            yaw_delta = data_this_worker1.yaw(delta_sensors=True, delta_time=True)

            worker_name = map_name(data_this_worker1.worker_name)

            print("Processing {}...".format(worker_name))

            # angular velocity
            omega = pd.DataFrame(yaw_delta, columns=['delta_angle'])
            omega['delta_time'] = time_delta.values
            omega['omega'] = omega['delta_angle'] / omega['delta_time']
            omega = omega[omega['delta_angle'].abs() > 5]
            omega['omega'] = omega[(omega['omega'] > -2000) & (omega['omega'] < 2000)]

            omega = omega[(~np.isnan(omega['omega']))]

            # plt.figure()
            # plt.subplot(221)
            # plt.plot(time_delta.values, yaw_delta, 'b.')
            # plt.subplot(222)
            # plt.plot(omega['omega'], 'r.')
            # plt.subplot(223)
            # plt.plot(omega['delta_angle'], 'g.')
            # plt.show()

            metric1, std = compute_metric(omega=omega)
            metric1 = std

            sns.distplot(omega['omega'], label=worker_name + ' = {:.0f}'.format(metric1))
            plt.xlim(-180, 180)
            plt.ylim(0, 0.04)
            plt.xlabel(None)
            plt.ylabel('Density')
            plt.title(task + '- segment 1')
            plt.grid(True)
            plt.legend(loc='best')

            plt.subplot(212)
            time_delta = data_this_worker2.time_delta
            yaw_delta = data_this_worker2.yaw(delta_sensors=True, delta_time=True)

            # angular velocity
            omega = pd.DataFrame(yaw_delta, columns=['delta_angle'])
            omega['delta_time'] = time_delta.values
            omega['omega'] = omega['delta_angle'] / omega['delta_time']
            omega = omega[omega['delta_angle'].abs() > 5]
            omega['omega'] = omega[(omega['omega'] > -2000) & (omega['omega'] < 2000)]
            omega = omega[(~np.isnan(omega['omega']))]

            # compute single metric:
            metric2, std = compute_metric(omega=omega)
            metric2 = std

            # plt.figure()
            # plt.subplot(221)
            # plt.plot(time_delta.values, yaw_delta, 'b.')
            # plt.subplot(222)
            # plt.plot(omega['omega'], 'r.')
            # plt.subplot(223)
            # plt.plot(omega['delta_angle'], 'g.')
            # plt.show()

            sns.distplot(omega['omega'], label=worker_name + ' = {:.0f}'.format(metric2))
            plt.xlim(-180, 180)
            plt.ylim(0, 0.04)
            plt.xlabel('Angular velocity (deg/s)')
            plt.ylabel('Density')
            plt.title(task + '- segment 2')
            plt.grid(True)
            plt.legend(loc='best')

            final_metric = np.sqrt(metric1 ** 2 + metric2 ** 2)

            metric_per_worker[task][worker_name] = final_metric

            #
            import matplotlib.pyplot as P
            import matplotlib

            # angle = np.clip(omega['delta_angle'], -90, 90)
            # angle = np.clip(omega['delta_angle'], 0, 90)
            # omega = omega['omega']

            # sp = P.subplot(1, 1, 1, projection='polar')
            # conv = (np.pi / 180.)
            # # sp.set_thetamin(-90 * conv)
            # # sp.set_thetamax(90 * conv)
            # ones = np.ones(len(angle))
            # sp.set_theta_offset(90 * conv)
            # plt.thetagrids([theta * 15 for theta in range(360 // 15)])
            # P.plot(angle, ones, '.')

            # # Set up a grid of axes with a polar projection
            # g = sns.FacetGrid(omega, col="delta_angle", hue="omega",
            #                   subplot_kws=dict(projection='polar'), height=4.5,
            #                   sharex=False, sharey=False, despine=False)
            # g.map(sns.scatterplot, "theta", "r")

            # break

        return metric_per_worker
