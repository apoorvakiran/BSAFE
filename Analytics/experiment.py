# -*- coding: utf-8 -*-
"""
Holds an Experiment.

@ author Jesper Kristensen
Copyright 2018
"""

__all__ = ["Experiments", "Experiment"]
__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import os
import datetime
import glob
import pickle
import scipy
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import UnivariateSpline
from Analytics import LoadData


class Experiments(object):
    """
    Holds multiple experiments at the same time.
    From this, we can, e.g., retrieve the yaw data across all experiments etc.
    """

    _experiments = None
    _all_workers = None
    _all_segments = None
    _all_hands = None
    _all_tasks = None
    _good_files =  None
    _bad_files = None

    def __init__(self, basepath=None, is_structured=False, list_of_filenames=None, cache_path='cache_experiments.pkl'):
        """
        From a list of incoming files, construct a set of experiments
        :param basepath:
        :param is_structured: Specify whether the data is structured in the pre-specified
        format "Day --> "Task" --> ...
        :param list_of_filenames:
        """

        if not is_structured and list_of_filenames is None:
            raise Exception("Your input: The data is not structured and there is no list of filenames provided?\n"
                            "Please provide at least one of the two!")

        if os.path.isfile(cache_path):
            print("Loading experiments from cache at location '{}'".format(cache_path))

            with open(cache_path, 'rb') as fd:
                cache = pickle.load(fd)

            experiments = cache['experiments']
            self._good_files = cache['good_files']
            self._bad_files = cache['bad_files']

        else:
            print("Cache not found at location '{}', computing from scratch".format(cache_path))

            if is_structured:
                experiments, good_files, bad_files = self._load_structured_data(basepath=basepath)
                print("Structured data loaded.")
            else:
                # not structured per se, just load the list of incoming files
                if list_of_filenames is None or len(list_of_filenames) < 1 or not isinstance(list_of_filenames[0], str):
                    raise Exception("Please provide a valid input for the list of filenames instead of '{}'".
                                    format(list_of_filenames))

                good_files = []
                bad_files = {}
                experiments = []
                for fn in list_of_filenames:
                    try:
                        exp = Experiment(path=os.path.join(basepath, fn),
                                                  name=os.path.splitext(fn)[0],
                                                  destination='.')
                        good_files.append(os.path.split(fn)[1])
                        experiments.append(exp)
                    except Exception as e:
                        bad_files[os.path.split(fn)[1]] = e



                self._good_files = good_files
                self._bad_files = bad_files

            if cache_path is None:
                cache_path = 'cache.pkl'

            cache = {'experiments': experiments, 'good_files': good_files, 'bad_files': bad_files}
            with open(cache_path, 'wb') as fd:
                pickle.dump(cache, fd)

            print("Stored the results in cache '{}'".format(cache_path))

        self._experiments = experiments

        print("Loaded {} experiments!".format(len(self._experiments)))

        if len(self._experiments) == 0:
            raise Exception("There were no experiments loaded?")

        self._all_workers = list(np.unique([exp.meta_data['worker'].lower().strip().replace(' ', '') for exp in self._experiments]))
        self._all_segments = list(np.unique([exp.meta_data['segment'].lower().strip().replace(' ', '') for exp in self._experiments]))
        self._all_hands = list(np.unique([exp.meta_data['hand'].lower().strip().replace(' ', '') for exp in self._experiments]))
        self._all_tasks = list(np.unique([exp.meta_data['task_name'].lower().strip().replace(' ', '') for exp in self._experiments]))

        print("Number of good files = {}".format(len(self.good_files)))
        print("Number of bad files = {}".format(len(self.bad_files)))
        print("Percent good files = {:.1f}% (#={})".format(
            len(self.good_files) / (len(self.good_files) + len(self.bad_files)) * 100,
            len(self.good_files)))

        # TODO: Here we can create maps from, say, worker to tasks, to segments, etc.

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

                            for exp in self._experiments:

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

    def _load_structured_data(self, basepath=None):
        """
        Loads the structured data.

        :param basepath:
        :return:
        """
        all_experiments = []
        all_days_init = glob.glob(os.path.join(basepath, '*'))
        all_days_used = []
        good_files = []
        bad_files = {}
        for day in all_days_init:
            # for each day...

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
                    all_datafiles_this_worker = glob.glob(os.path.join(worker_this_day_this_task, '{}_*.csv'.format(day_name)))

                    # extract hand information and job segment (each segment is in between breaks etc.):
                    for file in all_datafiles_this_worker:

                        basename_list = os.path.splitext(os.path.split(file)[1])[0].split('_')

                        hand = basename_list[-1]
                        segment = basename_list[-2]

                        assert basename_list[0].lower() == day_name.lower()
                        assert basename_list[2].lower() == task_name.lower()
                        assert basename_list[3].lower() == worker_name.lower()

                        # Data for this day, this task, this worker, this hand & segment
                        # loaded in a robust way:
                        # try:
                        try:
                            this_exp = Experiment(path=file, name=os.path.splitext(os.path.split(file)[1])[0],
                                                  meta_data={'hand': hand, 'segment': segment, 'worker': worker_name,
                                                             'task_name': task_name, 'filename': file,
                                                             'basepath': basepath,
                                                             'date_loaded': datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')})
                        except Exception as e:
                            print("There was an error '{}' in loading the data at {}, continuing...".format(e, os.path.split(file)[1]))
                            # import pdb
                            # pdb.set_trace()
                            bad_files[os.path.split(file)[1]] = e
                            continue

                        good_files.append(os.path.split(file)[1])
                        all_experiments.append(this_exp)

        self._good_files = good_files
        self._bad_files = bad_files

        return all_experiments, good_files, bad_files

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

            list_of_exps = [exp for exp in self._experiments if \
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

            list_of_exps = [exp for exp in self._experiments if \
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
        all_yaw = [exp.yaw(loc=loc, delta=delta) for exp in self._experiments]

        # final_yaw =

        import pdb
        pdb.set_trace()


class Experiment(object):
    """
    This class represents a single experiment holding the data and we can retrieve
    specific data from it and ask it to calculate various quantities.
    """

    _name = None
    _time = None

    _yaw = None
    _pitch = None
    _roll = None

    _ax = None
    _ay = None
    _az = None

    _meta_data = None

    def __init__(self, path=None, destination=None, name=None, meta_data=None):
        """
        Construct an experiment class.

        :param path:
        :param destination:
        """

        self._name = name

        dataloader = LoadData()
        data = dataloader.get_data(path=path, destination=destination)

        self._time = pd.to_datetime(data['Date-Time'])

        self._yaw = dict()
        self._pitch = dict()
        self._roll = dict()

        self._yaw['hand'] = data['Yaw[0](deg)'].astype(float)
        self._yaw['wrist'] = data['Yaw[1](deg)'].astype(float)
        self._yaw['delta'] = self._yaw['wrist'] - self._yaw['hand']

        #
        self._pitch['hand'] = data['Pitch[0](deg)'].astype(float)
        self._pitch['wrist'] = data['Pitch[1](deg)'].astype(float)
        self._pitch['delta'] = self._pitch['wrist'] - self._pitch['hand']
        #
        self._roll['hand'] = data['Roll[0](deg)'].astype(float)
        self._roll['wrist'] = data['Roll[1](deg)'].astype(float)
        self._roll['delta'] = self._roll['wrist'] - self._roll['hand']

        self._ax = dict()
        self._ay = dict()
        self._az = dict()
        #
        if 'ax[0](mg)' in data:
            self._ax['hand'] = data['ax[0](mg)'].astype(float)
            self._ax['wrist'] = data['ax[1](mg)'].astype(float)
            #
            self._ay['hand'] = data['ay[0](mg)'].astype(float)
            self._ay['wrist'] = data['ay[1](mg)'].astype(float)
            #
            self._az['hand'] = data['az[0](mg)'].astype(float)
            self._az['wrist'] = data['az[1](mg)'].astype(float)
        else:
            print("Raw acceleration data not included!")

        self._gx = dict()
        self._gy = dict()
        self._gz = dict()
        #
        self._gx['hand'] = data['gx[0](dps)'].astype(float)
        self._gx['wrist'] = data['gx[1](dps)'].astype(float)
        #
        self._gy['hand'] = data['gy[0](dps)'].astype(float)
        self._gy['wrist'] = data['gy[1](dps)'].astype(float)
        #
        self._gz['hand'] = data['gz[0](dps)'].astype(float)
        self._gz['wrist'] = data['gz[1](dps)'].astype(float)

        self._meta_data = meta_data

    @property
    def meta_data(self):
        return self._meta_data

    @property
    def name(self):
        return self._name

    @property
    def time(self):
        """
        The time associated with the measurements.

        :return:
        """
        return self._time

    def _scale(self, data=None):
        return (np.asarray(data) - 0) / (360 - 0)

    def _unscale(self, scaled_data=None):
        return np.asarray(scaled_data) * (360 - 0) + 0

    def scale_to_angles(self, data=None):
        deg1_unscaled = 1
        deg1_scaled = self._scale(data=[deg1_unscaled])

        return data / deg1_scaled

    def _transform(self, data=None):
        """
        Quadrant fix. Put all angles in [0, 90].
        # TODO: Might need improvement...

        :param data:
        :return:
        """
        return data
        # return np.degrees(np.arcsin(np.sin(np.radians(data))))

    def get_data(self, type='yaw', loc='hand', interpolate=True, delta=False):

        if type == 'yaw':
            data = self.yaw(loc=loc, interpolate=interpolate, delta=delta)
        elif type == 'pitch':
            data = self.pitch(loc=loc, delta=delta)
        elif type == 'roll':
            data = self.roll(loc=loc, delta=delta)
        else:
            raise Exception("This is an unknown data type '{}'!".format(type))

        return self._transform(data)

    def yaw(self, loc='hand', delta=False, interpolate=True):
        """
        Measures the yaw.

        :param loc:
        :return:
        """
        # raw_data = self._yaw[loc].values.reshape(-1, 1)
        #
        # # standardize
        # raw_data_scaled = self._scale(raw_data)
        #
        # raw_10deg = 10
        # raw_1deg = 1
        #
        # scaled_10deg = self._scale([raw_10deg])
        # scaled_1deg = self._scale([raw_1deg])
        #
        # x = np.arange(len(raw_data_scaled))
        #
        # yaw_data = savgol_filter(raw_data_scaled.reshape(1, -1), 11, 4)
        #
        # df = pd.DataFrame(data=np.vstack([x, yaw_data]).T, columns=['Time', "Yaw"])
        # df = df.rolling(11).mean()
        #
        # level_zero = np.mean(df.loc[:280, 'Yaw'])
        # df.loc[:, 'Yaw'] = df.loc[:, 'Yaw'] - level_zero
        #
        # plt.figure()
        # plt.subplot(211)
        # plt.title("Raw Data")
        # plt.plot(x, raw_data, 'bx', zorder=1)
        # plt.axvline(280)
        # plt.grid()
        #
        # plt.subplot(212)
        # plt.title("Processed data")
        # plt.plot(df['Time'] / 10, self.scale_to_angles(data=df['Yaw']), 'r-', zorder=2)
        # plt.axhline(10, linestyle='--', color='k')
        # plt.axhline(20, linestyle='--', color='k')
        # plt.axhline(30, linestyle='--', color='k')
        # plt.xlabel("Time (s)")
        # plt.ylabel("Angle (deg)")
        # plt.grid()
        # plt.tight_layout()
        #
        # plt.figure()
        #
        # max_y_level = self.scale_to_angles(data=df['Yaw']).max()
        #
        # # plt.subplot(211)
        # # plt.title("Processed data")
        # # plt.plot(df['Time'] / 10, self.scale_to_angles(data=df['Yaw']), 'r-', zorder=2)
        # # plt.axhline(10, linestyle='--', color='k')
        # # plt.axhline(20, linestyle='--', color='k')
        # # plt.axhline(30, linestyle='--', color='k')
        # # plt.xlabel("Time (s)")
        # # plt.ylabel("Angle (deg)")
        # # plt.grid()
        #
        # # plt.subplot(212)
        # x = df['Time'] / 10
        # rula_threshold = 15
        # plt.plot(x, self.scale_to_angles(data=df['Yaw']), 'r-', zorder=2)
        # # plt.axhline(rula_threshold, linestyle='--', color='k')
        #
        # plt.axhspan(0, rula_threshold * 0.8, color='g', alpha=0.2)
        # plt.axhspan(rula_threshold * 0.8, rula_threshold, color='y', alpha=0.2)
        # plt.axhspan(rula_threshold, max_y_level, color='r', alpha=0.2)
        #
        # plt.xlabel("Time (s)")
        # plt.ylabel("Angle (deg)")
        # plt.grid()
        # plt.tight_layout()
        #
        # plt.show()

        if delta:
            return self._yaw['delta']

        return self._yaw[loc]

    def pitch(self, loc='hand', delta=False):
        """
        Measures the pitch.

        :param loc:
        :return:
        """
        if delta:
            return self._pitch['delta']

        return self._pitch[loc]

    def roll(self, loc='hand', delta=False):
        """
        Measures the roll.

        :param loc:
        :return:
        """
        if delta:
            return self._roll['delta']

        return self._roll[loc]

    def ax(self, loc='hand'):
        """
        Returns the linear accelerations along x.

        :param loc:
        :return:
        """
        if loc in self._ax:
            return self._ax[loc]

    def ay(self, loc='hand'):
        """
        Returns the linear accelerations along y.

        :param loc:
        :return:
        """
        if loc in self._ay:
            return self._ay[loc]

    def az(self, loc='hand'):
        """
        Returns the linear accelerations along z.

        :param loc:
        :return:
        """
        if loc in self._az:
            return self._az[loc] / 1000 - 1  # subtract gravity

    def gx(self, loc='hand'):
        """
        Angular velocity around x-axis.

        :param loc:
        :return:
        """
        if loc in self._gx:
            return self._gx[loc]

    def gy(self, loc='hand'):
        """
        Angular velocity around y-axis.

        :param loc:
        :return:
        """
        if loc in self._gy:
            return self._gy[loc]

    def gz(self, loc='hand'):
        """
        Angular velocity around z-axis.

        :param loc:
        :return:
        """
        if loc in self._gz:
            return self._gz[loc]

    def angular_acc_x(self, loc='hand'):
        """
        Angular acceleration around x-axis.
     
        :param loc:
        :return:
        """
        # need to obtain this as derivative in time from the gyroscope data

        x = self.time
        w = self.gx(loc=loc)  # degrees per second (DPS) (angular velocity)

        x_conv = (pd.to_datetime(x) -
                  datetime.datetime(1970, 1, 1)).apply(lambda x: x.total_seconds())

        w_interp = UnivariateSpline(x_conv, w)  # w(t) --> velocity

        alpha_interp = w_interp.derivative(n=1)  # alpha = dw(t)/dt --> angular acceleration

        # plt.figure()
        # plt.plot(x, w, 'r--')
        # plt.plot(x, w_interp(x_conv), 'bx')
        # plt.show()
      
        return alpha_interp(x_conv)
        
        
    def quadCorrect(self, swing = 180):
     """
     Take an experiment object and reduce large swings in angle from measurement to measurement.
     swing is the maximum value by which an angle will be allowed to change in one timestep
     """
     #start by grabbing the length of the array
     lend=len(self._time)
     dictions=[self._yaw, self._pitch, self._roll]
     #these three dictionaries need to be checked and updated on multiple values
     n=1
     #Switching to np array objects, easier to perform updates here.
     self._yaw['hand']=np.array(self._yaw['hand'])
     self._yaw['wrist']=np.array(self._yaw['wrist'])
     self._yaw['delta']=np.array(self._yaw['delta'])
     self._pitch['hand']=np.array(self._pitch['hand'])
     self._pitch['wrist']=np.array(self._pitch['wrist'])
     self._pitch['delta']=np.array(self._pitch['delta'])
     self._roll['hand']=np.array(self._roll['hand'])
     self._roll['wrist']=np.array(self._roll['wrist'])
     self._roll['delta']=np.array(self._roll['delta'])
     while (n<lend) :
      for set in dictions:
        changed=False #set to true if changes are made, then update delta.
        #print(set.keys())
        handSwing=abs(set['hand'][n]-set['hand'][n-1])
        #print(handSwing)
        wristSwing=abs(set['wrist'][n]-set['wrist'][n-1])
        if (handSwing >swing):
          #print(set['hand'][n-1])
          set['hand'][n]=set['hand'][n-1] #sets it to the previous value (swing of 0)
          #print(set['hand'][n])
          changed=True
        if (wristSwing>swing):
          set['wrist'][n]=set['wrist'][n-1]
          changed=True
        if changed:
          set['delta'][n]=set['wrist'][n]-set['hand'][n]
        #print('Updated quadrant for value ' + str(n))
        #print(handSwing)
        #print(wristSwing)
      n=n+1
    #Transferring between Series and np.array objects, back to a Series.
     self._yaw['hand']=pd.Series(self._yaw['hand'])
     self._yaw['wrist']=pd.Series(self._yaw['wrist'])
     self._yaw['delta']=pd.Series(self._yaw['delta'])
     self._pitch['hand']=pd.Series(self._pitch['hand'])
     self._pitch['wrist']=pd.Series(self._pitch['wrist'])
     self._pitch['delta']=pd.Series(self._pitch['delta'])
     self._roll['hand']=pd.Series(self._roll['hand'])
     self._roll['wrist']=pd.Series(self._roll['wrist'])
     self._roll['delta']=pd.Series(self._roll['delta'])
     return(self) 

    def truncate(self, lowEnd, highEnd):
      """
      Going to truncate to just the low:high values in the data ranges.
      """
      for key in self._yaw:
         self._yaw[key]=self._yaw[key][lowEnd:highEnd]
            
      for key in self._pitch:
          self._pitch[key]=self._pitch[key][lowEnd:highEnd]
            
      for key in self._roll:
         self._roll[key]=self._roll[key][lowEnd:highEnd]
          
      for key in self._ax:
         self._ax[key]=self._ax[key][lowEnd:highEnd]
            
      for key in self._ay:
         self._ay[key]=self._ay[key][lowEnd:highEnd]
         
      for key in self._az:
            self._az[key]=self._az[key][lowEnd:highEnd]
          
      self._time=self._time[lowEnd:highEnd]
          
      return(self)

    def topAndBottom(self):
     """
     Toss an experiment at this, it will return a truncated experiment
     Discards values until a point where standard deviation has been higher for 30 seconds
     than it was in the first 10 seconds, for both pitch and yaw.
     Does the same for the end of the list, discarding the end values.
     """
     yawDel=self.get_data(type='yaw', delta=True)
     startYawDev=scipy.std(yawDel[0:100])
     pitchDel=self.get_data(type='pitch', delta=True)
     startPitchDev=scipy.std(pitchDel[0:100])
     n=0
     lastThreeYaw=[0,0,0]
     lastThreePitch=[0,0,0]
     while (startYawDev>=lastThreeYaw[0] or \
        startYawDev>=lastThreeYaw[1] or \
        startYawDev>=lastThreeYaw[2] or \
        startPitchDev>=lastThreePitch[0] or \
        startPitchDev>=lastThreePitch[1] or \
        startPitchDev>=lastThreePitch[2]):
        highEnd=n+99
        lastThreeYaw.pop(0)
        lastThreePitch.pop(0)
        lastThreeYaw.append(scipy.std(yawDel[n:highEnd]))
        lastThreePitch.append(scipy.std(pitchDel[n:highEnd]))
        #print(startPitchDev)
        #print(lastThreePitch)
        #print(startYawDev)
        #print(lastThreeYaw)
        n=n+100
     startPoint=n-200
     #print(startPoint)
     #print(n)
     n=-1
     lastThreeYaw=[0,0,0]
     lastThreePitch=[0,0,0]
     while (startYawDev>=lastThreeYaw[0] or \
        startYawDev>=lastThreeYaw[1] or \
        startYawDev>=lastThreeYaw[2] or \
        startPitchDev>=lastThreePitch[0] or \
        startPitchDev>=lastThreePitch[1] or \
        startPitchDev>=lastThreePitch[2]):
        lowEnd=n-99
        lastThreeYaw.pop(0)
        lastThreePitch.pop(0)
        lastThreeYaw.append(scipy.std(yawDel[lowEnd:n]))
        lastThreePitch.append(scipy.std(pitchDel[lowEnd:n]))
        n=n-100
     endPoint=n+200
     #print(''+str(startPoint) + '  , ' + str(endPoint))
     return(self.truncate(startPoint,endPoint))
   