# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["Rula"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
import matplotlib

font = {'family': 'normal', 'size': 12}
matplotlib.rc('font', **font)


class Rula(object):
    """
    Basic RULA analysis real-time.
    """

    _experiments = None

    def __init__(self, experiments=None):

        self._experiments = np.atleast_1d(experiments)

        all_scores = []
        plt = None
        for exp_ix, experiment in enumerate(self._experiments):

            # YAW:
            time, scores_yaw = self._construct_yaw_rula(experiment=experiment)
            self._summarize_rula(scores=scores_yaw, exp_ix=exp_ix)

            time, scores_pitch = self._construct_pitch_rula(experiment=experiment)
            self._summarize_rula(scores=scores_pitch, exp_ix=exp_ix)

            # ROLL:
            time, scores_roll = self._construct_roll_rula(experiment=experiment)
            self._summarize_rula(scores=scores_roll, exp_ix=exp_ix)

            time, scores_yaw = self._construct_rula_scores(type='yaw', experiment=experiment)

            # PITCH:
            time, scores_pitch = self._construct_rula_scores(type='pitch', experiment=experiment)

            # ROLL:
            time, scores_roll = self._construct_rula_scores(type='roll', experiment=experiment)

            scores_roll.loc[(np.abs(scores_roll[0]) < 15), 'scores'] = 1
            scores_roll.loc[(np.abs(scores_roll[0]) >= 15), 'scores'] = 2

            # total score:
            total_scores = scores_yaw.copy()
            total_scores['total'] = scores_yaw['scores'] + scores_pitch['scores'] + scores_roll['scores']

            if plt is None:
                import matplotlib.pyplot as plt
                import seaborn as sns
                plt.figure()
                sns.set(style="whitegrid")

            total_scores['exp'] = exp_ix
            # total_scores['within_exp_score'] = total_scores['scores']

            all_scores.append(total_scores)

            plt.subplot(211)
            plt.hist(total_scores['total'], bins=20, label=experiment.name)
            plt.hist(total_scores['total'], bins=20, alpha=0.4, label=experiment.name)
            plt.xlabel('RULA score')
            plt.ylabel('count')
            plt.grid()

            plt.subplot(212)
            # import pdb
            # pdb.set_trace()
            # total_scores['time'] = time.index
            plt.plot(total_scores.index, total_scores['total'], '.')
            plt.xlabel('time')
            plt.ylabel('RULA score')
            plt.grid()

        plt.subplot(211)
        plt.legend(loc='best')
        plt.show()

        import pandas as pd
        all_scores = pd.concat(all_scores)

        plt.figure()
        for exp, (gix, gdata) in zip(experiments, all_scores.groupby('exp')):
            plt.hist(gdata['total'], label=exp.name)
            plt.xlabel('RULA')
            plt.ylabel('counts')
            print(gdata['total'].median())

        plt.grid()
        plt.legend(loc='best')
        plt.savefig('rula.png')

        # TODO: Maybe the RULA should be defined slightly differently.
        # maybe saying "if the hand is beyond certain angle for so much time
        # then you get a tick. In other words, there's a "clock that starts" after
        # so and so much time beyond 15 degrees. Or else the rula oscillates
        # way too quickly. But then another measure can be how rapidly the hand
        # moves as a frequency as well (so do capture the rapid movements too).

        plt.figure()
        all_data = []
        for exp, (gix, gdata) in zip(experiments, all_scores.groupby('exp')):

            this_data = gdata['total'].iloc[2150:2180]
            plt.plot(this_data, '-', label=exp.name, linewidth=2)

            plt.xlabel('time [.]')
            plt.ylabel('RULA')

            all_data.append(this_data)

            print('*' * 12)
            print(exp.name)

            # # for this person, try these:
            # # now look at how this move over segments of the data:
            # window_size = 3600
            # for j in [0, 1, 2]:
            #     print('----')
            #     this_data = gdata['total'][j * window_size:(j + 1) * window_size]
            #     print(this_data.mean())
            #     perc = (np.abs(gdata[0][j * window_size:(j + 1) * window_size]) > 15).sum() / gdata[0][j * window_size:(j + 1) * window_size].count() * 100
            #     print(perc)
            #     print(gdata[0][j * window_size:(j + 1) * window_size].count() / 2 * perc / 100 / 60)

        compute_average = pd.concat(all_data, axis=1)
        compute_average = compute_average.mean(axis=1)

        plt.plot(compute_average, 'k--', label='avg', linewidth=2)

        plt.grid('on')
        plt.legend(loc='best')
        plt.savefig('rula_vs_time.png')
        # plt.show()

        # # demonstrate some plots
        # plt.figure()
        # plt.plot(gdata['total'][2100:2600], '.', label=exp.name)
        # plt.grid()
        # plt.xlabel('time [.]')
        # plt.ylabel('RULA')
        # plt.show()

    def _summarize_rula(self, scores=None, exp_ix=None, threshold_degrees=15):
        """

        :param scores:
        :param exp_ix:
        :param threshold_degrees:
        :return:
        """
        print("=== Experiment {} ===".format(exp_ix))
        print("Analysis:")
        print('Median = {}'.format(scores['scores'].median()))
        perc = (np.abs(scores[0]) > threshold_degrees).sum() / scores[0].count() * 100
        print('% > {} = {}'.format(threshold_degrees, perc))
        print('time > {} = {} min.'.format(threshold_degrees, len(scores) / 2 * perc / 100 / 60))

    def _construct_roll_rula(self, experiment=None):

        time = experiment.time

        # separate out a chunk of data that looks good
        # from_ = 4000
        # till_ = 15000
        # if you want to use all data:
        from_ = time.index[0]
        till_ = time.index[-1]

        yaw_hand = experiment.get_data(type='yaw', loc='hand')
        yaw_wrist = experiment.get_data(type='yaw', loc='wrist')

        time = time.iloc[from_:till_]

        yaw_hand = yaw_hand.iloc[from_:till_]
        yaw_wrist = yaw_wrist.iloc[from_:till_]
        delta_yaw = (yaw_hand - yaw_wrist).iloc[from_:till_]

        # hand = go.Scatter(x=yaw_hand.index, y=yaw_hand)
        # wrist = go.Scatter(x=yaw_wrist.index, y=yaw_wrist)
        # delta = go.Scatter(x=delta_yaw.index, y=delta_yaw)
        # fig = go.Figure(data=[hand, wrist, delta])
        # plot(fig, auto_open=True)

        hi = np.percentile(delta_yaw, 99.9)
        lo = np.percentile(delta_yaw, 0.1)
        delta_yaw = np.clip(delta_yaw, lo, hi)

        scores = delta_yaw.to_frame()
        scores['scores'] = 0

        scores.loc[(np.abs(delta_yaw) <= 15), 'scores'] = 1
        scores.loc[(np.abs(delta_yaw) > 15), 'scores'] = 2

        return time, scores

    def _construct_yaw_rula(self, experiment=None):

        import pdb
        pdb.set_trace()

        # # plt.subplot(211)
        import matplotlib.pyplot as plt
        import seaborn as sns
        plt.figure()
        sns.set(style="whitegrid")
        # g = sns.catplot(x="total", y='within_exp_score', hue="exp", data=all_scores, height=6, kind="bar", palette="muted")
        # g = sns.catplot(x="total", data=total_scores, height=6, kind="bar", palette="muted")


        sns.barplot(x="total", y='exp', hue="exp", data=all_scores)

        plt.show()
        # import pdb
        # pdb.set_trace()
        #
        import pdb
        pdb.set_trace()

    def _construct_rula_scores(self, type='yaw', experiment=None, levels=None, scores=None, time=None):

        time = experiment.time

        # separate out a chunk of data that looks good
        # from_ = 4000
        # till_ = 15000
        # if you want to use all data:
        from_ = time.index[0]
        till_ = time.index[-1]

        yaw_hand = experiment.get_data(type='yaw', loc='hand')
        yaw_wrist = experiment.get_data(type='yaw', loc='wrist')

        time = time.iloc[from_:till_]

        yaw_hand = yaw_hand.iloc[from_:till_]
        yaw_wrist = yaw_wrist.iloc[from_:till_]
        delta_yaw = (yaw_hand - yaw_wrist).iloc[from_:till_]

        # hand = go.Scatter(x=yaw_hand.index, y=yaw_hand)
        # wrist = go.Scatter(x=yaw_wrist.index, y=yaw_wrist)
        # delta = go.Scatter(x=delta_yaw.index, y=delta_yaw)
        # fig = go.Figure(data=[hand, wrist, delta])
        # plot(fig, auto_open=True)

        hi = np.percentile(delta_yaw, 99.9)
        lo = np.percentile(delta_yaw, 0.1)
        delta_yaw = np.clip(delta_yaw, lo, hi)

        scores = delta_yaw.to_frame()
        scores['scores'] = 0

        scores.loc[(np.abs(delta_yaw) <= 5), 'scores'] = 0
        scores.loc[(np.abs(delta_yaw) > 5), 'scores'] = 1

        return time, scores

    def _construct_pitch_rula(self, experiment=None, levels=None, scores=None, time=None):

        time = experiment.time

        # separate out a chunk of data that looks good
        # from_ = 4000
        # till_ = 15000
        # if you want to use all data:
        from_ = time.index[0]
        till_ = time.index[-1]

        yaw_hand = experiment.get_data(type='pitch', loc='hand')
        yaw_wrist = experiment.get_data(type='pitch', loc='wrist')
        yaw_hand = experiment.get_data(type=type, loc='hand')
        yaw_wrist = experiment.get_data(type=type, loc='wrist')

        time = time.iloc[from_:till_]

        yaw_hand = yaw_hand.iloc[from_:till_]
        yaw_wrist = yaw_wrist.iloc[from_:till_]
        delta_yaw = (yaw_hand - yaw_wrist).iloc[from_:till_]

        # hand = go.Scatter(x=yaw_hand.index, y=yaw_hand)
        # wrist = go.Scatter(x=yaw_wrist.index, y=yaw_wrist)
        # delta = go.Scatter(x=delta_yaw.index, y=delta_yaw)
        # fig = go.Figure(data=[hand, wrist, delta])
        # plot(fig, auto_open=True)

        hi = np.percentile(delta_yaw, 99.9)
        lo = np.percentile(delta_yaw, 0.1)
        delta_yaw = np.clip(delta_yaw, lo, hi)

        scores = delta_yaw.to_frame()
        scores['scores'] = 0

        scores.loc[(np.abs(delta_yaw) <= 5), 'scores'] = 1
        scores.loc[(np.abs(delta_yaw) > 5) & (np.abs(delta_yaw) <= 15), 'scores'] = 2
        scores.loc[(np.abs(delta_yaw) > 15), 'scores'] = 3

        return time, scores

    # def _construct_rula_scores(self, type='yaw', experiment=None, levels=None, scores=None, time=None):
    #
    #     time = experiment.time
    #
    #     # separate out a chunk of data that looks good
    #     # from_ = 4000
    #     # till_ = 15000
    #     # if you want to use all data:
    #     from_ = time.index[0]
    #     till_ = time.index[-1]
    #
    #     yaw_hand = experiment.get_data(type=type, loc='hand')
    #     yaw_wrist = experiment.get_data(type=type, loc='wrist')
    #
    #     time = time.iloc[from_:till_]
    #
    #     yaw_hand = yaw_hand.iloc[from_:till_]
    #     yaw_wrist = yaw_wrist.iloc[from_:till_]
    #     delta_yaw = (yaw_hand - yaw_wrist).iloc[from_:till_]
    #
    #     # hand = go.Scatter(x=yaw_hand.index, y=yaw_hand)
    #     # wrist = go.Scatter(x=yaw_wrist.index, y=yaw_wrist)
    #     # delta = go.Scatter(x=delta_yaw.index, y=delta_yaw)
    #     # fig = go.Figure(data=[hand, wrist, delta])
    #     # plot(fig, auto_open=True)
    #
    #     hi = np.percentile(delta_yaw, 99.9)
    #     lo = np.percentile(delta_yaw, 0.1)
    #     delta_yaw = np.clip(delta_yaw, lo, hi)
    #
    #     scores = delta_yaw.to_frame()
    #     scores['scores'] = 0
    #
    #     scores.loc[(np.abs(delta_yaw) <= 5), 'scores'] = 1
    #     scores.loc[(np.abs(delta_yaw) > 5) & (np.abs(delta_yaw) <= 15), 'scores'] = 2
    #     scores.loc[(np.abs(delta_yaw) > 15), 'scores'] = 3
    #
    #     return time, scores
