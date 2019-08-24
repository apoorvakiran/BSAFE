# -*- coding: utf-8 -*-
"""
Holds a collection of structured datasets. From this, we can get all the yaw's
from various structured datasets and more easily navigate a set of data.

@ author Jesper Kristensen
Copyright 2018-
"""

__all__ = ["CollectionStructuredData"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import glob
import pickle
import datetime
import numpy as np
import pandas as pd
from . import StructuredDataStatic


class CollectionStructuredData(object):
    """
    Holds multiple structured datasets at the same time.
    From this, we can, e.g., retrieve the yaw data across all datasets etc.

    This is convenient if a task is broken into multiple (disjoint) datasets.
    """

    _data_format_code = None
    _structured_datasets = None
    _all_workers = None
    _all_segments = None
    _all_hands = None
    _all_tasks = None
    _good_files = None
    _bad_files = None

    def __init__(self, basepath=None, is_structured=False,
                 list_of_filenames=None, cache_path='cache_experiments.pkl',
                 ignore_cache=False, data_format_code='3'):
        """
        From a list of incoming files, construct a set of structured_datasets
        :param basepath:
        :param is_structured: Specify whether the data is structured in the pre-specified
        format "Day --> "Task" --> ...
        :param list_of_filenames:
        """

        if not is_structured and list_of_filenames is None:
            raise Exception("Your input: The data is not structured and "
                            "there is no list of filenames provided?\n"
                            "Please provide at least one of the two!")

        self._data_format_code = data_format_code

        if not ignore_cache and os.path.isfile(cache_path):
            print("Loading structured_datasets from cache at "
                  "location '{}'".format(cache_path))

            with open(cache_path, 'rb') as fd:
                cache = pickle.load(fd)

            structured_datasets = cache['structured_datasets']
            self._good_files = cache['good_files']
            self._bad_files = cache['bad_files']

        else:
            if ignore_cache:
                print("Cache is ignored. Compute from scratch.")
            else:
                print("Cache not found at location '{}', computing from "
                      "scratch".format(cache_path))

            if is_structured:
                structured_datasets, good_files, bad_files = \
                    self._load_structured_data(basepath=basepath,
                                               data_format_code=data_format_code)
                print("Structured data loaded.")
            else:
                # not structured per se, just load the list of incoming files
                print('Trying to use the list of names')
                if list_of_filenames is None or len(list_of_filenames) < 1 or \
                        not isinstance(list_of_filenames[0], str):
                    raise Exception("Please provide a valid input for the "
                                    "list of filenames instead of '{}'".
                                    format(list_of_filenames))

                good_files = []
                bad_files = {}
                structured_datasets = []
                for fn in list_of_filenames:
                    try:
                        exp = StructuredDataStatic(path=os.path.join(basepath,
                                                                     fn),
                                                   name=os.path.splitext(fn)[0],
                                                   destination='.')
                        import pdb
                        pdb.set_trace()
                        good_files.append(os.path.split(fn)[1])
                        structured_datasets.append(exp)
                    except Exception as e:
                        bad_files[os.path.split(fn)[1]] = e

                self._good_files = good_files
                self._bad_files = bad_files

            if cache_path is None:
                cache_path = 'cache.pkl'

            cache = {'structured_datasets': structured_datasets,
                     'good_files': good_files, 'bad_files': bad_files}
            with open(cache_path, 'wb') as fd:
                pickle.dump(cache, fd)

            print("Stored the results in cache '{}'".format(cache_path))

        self._structured_datasets = structured_datasets

        print("Loaded {} structured datasets!".format(
            len(self._structured_datasets)))

        if len(self._structured_datasets) == 0:
            raise Exception("There were no structured datasets loaded?")

        self._all_workers = list(
            np.unique([exp.meta_data['worker'].lower().strip().replace(' ', '') for exp in self._structured_datasets]))
        self._all_segments = list(
            np.unique([exp.meta_data['segment'].lower().strip().replace(' ', '') for exp in self._structured_datasets]))
        self._all_hands = list(
            np.unique([exp.meta_data['hand'].lower().strip().replace(' ', '') for exp in self._structured_datasets]))
        self._all_tasks = list(
            np.unique([exp.meta_data['task_name'].lower().strip().replace(' ', '') for exp in self._structured_datasets]))

        print("Number of good files = {}".format(len(self.good_files)))
        print("Number of bad files = {}".format(len(self.bad_files)))
        print("Percent good files = {:.1f}% (#={})".format(
            len(self.good_files) / (len(self.good_files) + len(self.bad_files)) * 100,
            len(self.good_files)))

        # TODO: Here we can create maps from, say, worker to tasks, to segments, etc.

    def datasets(self):
        """
        Generator to iterate over structured datasets held in this collection.

        :return:
        """
        for exp in self._structured_datasets:
            yield exp

    def collect_data_and_vary(self, vary='task', type='yaw', loc=None, delta=True):

        # get all data except what to vary:
        if vary == 'task':

            # TODO: Put everything in DATAFRAME! Then do groupby(...)

            all_data = {}
            for task in self.all_tasks:
                all_data[task] = []

                for hand in self.all_hands:
                    for worker in self.all_workers:
                        for segment in self.all_segments:

                            for exp in self._structured_datasets:

                                if (exp.meta_data['hand'].lower().strip().replace(' ', '') == hand and
                                        exp.meta_data['worker'].lower().strip().replace(' ', '') == worker and
                                        exp.meta_data['segment'].lower().strip().replace(' ', '') == segment and
                                        exp.meta_data['task_name'].lower().strip().replace(' ', '') == task):
                                    all_data[task].append(exp.get_data(type=type, loc=loc, delta=delta))

        return all_data

    @property
    def good_files(self):
        return self._good_files

    @property
    def bad_files(self):
        return self._bad_files

    @property
    def all_tasks(self):
        return self._all_tasks

    @property
    def all_workers(self):
        return self._all_workers

    @property
    def all_segments(self):
        return self._all_segments

    @property
    def all_hands(self):
        return self._all_hands

    def _load_structured_data(self, basepath=None, data_format_code='3'):
        """
        Loads the structured data.

        :param basepath:
        :return:
        """
        all_structured_datasets = []
        all_days_init = glob.glob(os.path.join(basepath, '*'))

        all_days_used = []
        good_files = []
        bad_files = {}
        for day in all_days_init:
            # for each day data was collected... Wednesday, Thursday, ...

            if not os.path.isdir(day):
                continue

            all_days_used.append(day)

            day_name = os.path.split(day)[1]

            # get all tasks for this day:
            all_tasks_init_this_day = glob.glob(os.path.join(day, '*'))

            for task_this_day in all_tasks_init_this_day:
                # for each task on this day...

                if not os.path.isdir(task_this_day):
                    continue

                task_name = os.path.split(task_this_day)[1].replace(' ', '')

                # get all the workers this day this task
                all_workers_init_this_day_this_task = glob.glob(os.path.join(task_this_day, '*'))

                for worker_this_day_this_task in all_workers_init_this_day_this_task:

                    if not os.path.isdir(worker_this_day_this_task):
                        continue

                    worker_name = os.path.split(worker_this_day_this_task)[1]
                    all_datafiles_this_worker = glob.glob(
                        os.path.join(worker_this_day_this_task, '{}_*.csv'.format(day_name)))

                    # extract hand information and job segment (each segment is in between breaks etc.):
                    for file in all_datafiles_this_worker:

                        basename_list = os.path.splitext(os.path.split(file)[1])[0].split('_')

                        hand = basename_list[-1]
                        segment = basename_list[-2]

                        assert basename_list[0].lower() == day_name.lower()
                        # print(basename_list)
                        # print(task_name.lower())
                        assert basename_list[2].lower() == task_name.lower()
                        assert basename_list[3].lower() == worker_name.lower()

                        # Data for this day, this task, this worker, this hand & segment
                        # loaded in a robust way:
                        # try:
                        try:
                            this_structured_dataset = StructuredDataStatic(path=file, data_format_code=data_format_code,
                                                                           name=os.path.splitext(os.path.split(file)[1])[0],
                                                  meta_data={'hand': hand, 'segment': segment, 'worker': worker_name,
                                                             'task_name': task_name, 'filename': file,
                                                             'basepath': basepath,
                                                             'date_loaded': datetime.datetime.today().strftime(
                                                                 '%Y-%m-%d %H:%M:%S')})
                        except Exception as e:
                            print("There was an error '{}' in loading the data at {}, continuing...".format(e,
                                                                                                            os.path.split(
                                                                                                                file)[
                                                                                                                1]))
                            # import pdb
                            # pdb.set_trace()
                            bad_files[os.path.split(file)[1]] = e
                            continue

                        good_files.append(os.path.split(file)[1])
                        all_structured_datasets.append(this_structured_dataset)

        self._good_files = good_files
        self._bad_files = bad_files

        return all_structured_datasets, good_files, bad_files

    def collect(self, type='yaw', loc='hand', delta=False, combine=False,
                task_name=None, hand=None, worker=None, segment=None):
        """
        Collects all tasks with a common name.
        How to call:
            exps.collect(task_name='Membrane Skinner', hand='right', segment='1', type='yaw', delta=True)
        :param type:
        :param loc:
        :param delta:
        :param task_name:
        :return:
        """
        # now, which variables are fixed? We can have just one varying
        check = np.asarray([task_name, hand, worker, segment])
        # we can only have 1 None (that will be the varying dimension):
        if not len(np.where(check == None)[0]) == 1:
            raise Exception("Please call the collect method specifying 3 out of 4 parameters!")

        names = ['task', 'hand', 'worker', 'segment']
        vary_this = np.asarray(names)[np.where(check == None)[0]][0]

        if len(segment) == 1:
            assert int(segment)
            segment = f'segment{segment}'

        task_name = task_name.lower().strip().replace(' ', '')
        if vary_this == 'hand':

            list_of_exps = [exp for exp in self._structured_datasets if \
                            (exp.meta_data['task_name'].lower().strip().replace(' ', '') == task_name and
                             exp.meta_data['worker'].lower().strip().replace(' ', '') == worker and
                             exp.meta_data['segment'].lower().strip().replace(' ', '') == segment
                             )]

        elif vary_this == 'worker':

            # data all workers
            # data = [exp.get_data(type=type, loc=loc, delta=delta) for exp in self._experiments if \
            #         (exp.meta_data['task_name'].lower().strip().replace(' ', '') == task_name and
            #          exp.meta_data['hand'].lower().strip().replace(' ', '') == hand and
            #          exp.meta_data['segment'].lower().strip().replace(' ', '') == segment
            #          )]

            list_of_exps = [exp for exp in self._structured_datasets if \
                            (exp.meta_data['task_name'].lower().strip().replace(' ', '') == task_name and
                             exp.meta_data['hand'].lower().strip().replace(' ', '') == hand and
                             exp.meta_data['segment'].lower().strip().replace(' ', '') == segment
                             )]

        # now create each column as a separate worker
        list_of_data_values = [data.get_data(type=type, loc=loc, delta=delta) for data in list_of_exps]

        if combine:
            # put each varying dimension in a new column
            combined_data = pd.concat(list_of_data_values, axis=1, ignore_index=True)
            combined_data.dropna(how='any', inplace=True)
        else:
            combined_data = list_of_data_values

        return combined_data, list_of_exps

    def yaw(self, loc='hand', delta=False, combine=False):
        """
        Returns the yaw.
        :param loc:
        :param delta:
        :param combine:
        :return:
        """
        # all_yaw = [exp.yaw(loc=loc, delta=delta) for exp in
        #            self._structured_datasets]

        raise NotImplementedError("Implement me!")

    def printer(self, outfile):
        totalz = self.totaller()
        printed = open(outfile, 'w')

        printed.write(
            'Day, Shift, Task, Worker, Segment, Hand, Motion - Pitch, '
            'Motion - Yaw, Motion - Roll, Motion, Posture, Speed - Pitch, '
            'Speed - Yaw, Speed - Roll')

        printed.write('\n')
        for key in totalz:
            printed.write(key)
            printed.write("\n")
            scores = []
            for score in totalz[key]:
                scores.append(score)
            scores.sort(reverse=True)
            n = 0
            summary = [0, 0, 0, 0, 0, 0, 0, 0]
            while n < len(scores):
                for exp in totalz[key][scores[n]]:
                    metric = exp._metrics
                    motion = metric._motion
                    summary[0] = summary[0] + motion[0]
                    summary[1] = summary[1] + motion[1]
                    summary[2] = summary[2] + motion[2]
                    summary[3] = summary[3] + motion[3]
                    post = metric._posture
                    summary[4] = summary[4] + post
                    speeds = metric._speed
                    summary[5] = summary[5] + speeds[0]
                    summary[6] = summary[6] + speeds[1]
                    summary[7] = summary[7] + speeds[2]
                    name = exp.name.replace('_', ', ')
                    printed.write(name + ", " + str(motion[0]) + ", " + str(motion[1]) + ", " + str(motion[2]) + ", "
                                  + str(motion[3]) + ", " + str(post) + ", " + str(speeds[0]) + ", " +
                                  str(speeds[1]) + ", " + str(speeds[2]) + ", " + "\n")
                n = n + 1
            summary[0] = np.mean(summary[0]) / n
            summary[1] = np.mean(summary[1]) / n
            summary[2] = np.mean(summary[2]) / n
            summary[3] = np.mean(summary[3]) / n
            summary[4] = np.mean(summary[4]) / n
            summary[5] = np.mean(summary[5]) / n
            summary[6] = np.mean(summary[6]) / n
            summary[7] = np.mean(summary[7]) / n
            printed.write(",,,, ,, " + str(summary[0]) + ", " + str(summary[1]) + "," +
                          str(summary[2]) + ", " + str(summary[3]) + ", " + str(summary[4]) + ", " + str(summary[5]) +
                          ", " + str(summary[6]) + ", " + str(summary[7]) + "\n")
            printed.write("\n")
        printed.close()

    def totaller(self):
        rankings = {}
        for exp in self._structured_datasets:
            name = exp.name.split('_')
            task = name[2]
            score = exp._metrics._motion[3]
            if task not in rankings:
                rankings[task] = {}
                rankings[task][score] = [exp]
            else:
                if score not in rankings[task]:
                    rankings[task][score] = [exp]
                else:
                    rankings[task][score].append(exp)
        return rankings
