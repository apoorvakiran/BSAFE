# -*- coding: utf-8 -*-
"""
Handles reporting of Ergonomic Metrics and results to customers.

@ author Jacob Tyrrell and Jesper Kristensen
Copyright Iterate Labs 2018-
"""
import logging
from datetime import datetime
import requests

__all__ = ['ErgoReport']

logger = logging.getLogger()


class ErgoReport (object):
    """
    Feed a metrics object and a desired output type
    (string, HTTP request, csv), receive an output
    """

    _type = None
    _metrics = None
    _authorization = None
    _locationOut = None
    _id = None
    _sent = None

    def __init__(self, typ=None, mets=None, auth=None, outSpot=None, macID=None):
        self._type = typ
        self._metrics = mets
        self._authorization = auth
        self._locationOut = outSpot
        self._id = macID
        payload = self.htOut()
        if typ == 'http':
            try:
                headers = {
                    'Authorization': self._authorization}
                self._sent = requests.post(self._locationOut, headers=headers,
                                     data=payload)
                self._sent.raise_for_status()
            except Exception:
                logger.error("Failure to send request", exc_info=True)
        if typ == 'string':
            self.outString()
        if typ == 'csv':
            self.csvout()
            #create printer function that will create a csv output file.

    def htOut(self):
        payload_dict = {}
        payload_dict['mac'] = self._id
        payload_dict['speed_pitch_score'] = self._metrics._speed[0]
        payload_dict['speed_yaw_score'] = self._metrics._speed[1]
        payload_dict['speed_roll_score'] = self._metrics._speed[2]
        payload_dict['normalized_speed_pitch_score'] = self._metrics._speedNormal[0]
        payload_dict['normalized_speed_yaw_score'] = self._metrics._speedNormal[1]
        payload_dict['normalized_speed_roll_score'] = self._metrics._speedNormal[2]
        payload_dict['speed_score'] = self._metrics._speedScore
        payload_dict['strain_pitch_score'] = self._metrics._strain[0]
        payload_dict['strain_yaw_score'] = self._metrics._strain[1]
        payload_dict['strain_roll_score'] = self._metrics._strain[2]
        payload_dict['strain_score'] = self._metrics._strain[3]
        payload_dict['posture_pitch_score'] = self._metrics._posture[0]
        payload_dict['posture_yaw_score'] = self._metrics._posture[1]
        payload_dict['posture_roll_score'] = self._metrics._posture[2]
        payload_dict['posture_score'] = self._metrics._posture[3]
        payload_dict['safety_score'] = self._metrics._totalScore
        time = self._metrics._collection_structured_data_obj.time
        timeZero = time._index[0]
        timeEnd = time._index[-1]
        startTime = time[timeZero]
        endTime = time[timeEnd]
        payload_dict['start_time'] = startTime
        payload_dict['end_time'] = endTime
        analyzed = datetime.now().utcnow().isoformat()
        payload_dict['analyzed_at'] = analyzed
        return payload_dict

    def csvout(self):
        return

    def outString(self):
        return


    # def printer(self, outfile):
    #
    #     raise Exception("Move Me to Reporter class!")
    #
    #     totalz = self.totaller()
    #     printed = open(outfile, 'w')
    #
    #     printed.write(
    #         'Day, Shift, Task, Worker, Segment, Hand, Motion - Pitch, '
    #         'Motion - Yaw, Motion - Roll, Motion, Posture, Speed - Pitch, '
    #         'Speed - Yaw, Speed - Roll')
    #
    #     printed.write('\n')
    #     for key in totalz:
    #         printed.write(key)
    #         printed.write("\n")
    #         scores = []
    #         for score in totalz[key]:
    #             scores.append(score)
    #         scores.sort(reverse=True)
    #         n = 0
    #         summary = [0, 0, 0, 0, 0, 0, 0, 0]
    #         while n < len(scores):
    #             for exp in totalz[key][scores[n]]:
    #                 metric = exp._metrics
    #                 motion = metric._motion
    #                 summary[0] = summary[0] + motion[0]
    #                 summary[1] = summary[1] + motion[1]
    #                 summary[2] = summary[2] + motion[2]
    #                 summary[3] = summary[3] + motion[3]
    #                 post = metric._posture
    #                 summary[4] = summary[4] + post
    #                 speeds = metric._speed
    #                 summary[5] = summary[5] + speeds[0]
    #                 summary[6] = summary[6] + speeds[1]
    #                 summary[7] = summary[7] + speeds[2]
    #                 name = exp.name.replace('_', ', ')
    #                 printed.write(name + ", " + str(motion[0]) + ", " + str(motion[1]) + ", " + str(motion[2]) + ", "
    #                               + str(motion[3]) + ", " + str(post) + ", " + str(speeds[0]) + ", " +
    #                               str(speeds[1]) + ", " + str(speeds[2]) + ", " + "\n")
    #             n = n + 1
    #         summary[0] = np.mean(summary[0]) / n
    #         summary[1] = np.mean(summary[1]) / n
    #         summary[2] = np.mean(summary[2]) / n
    #         summary[3] = np.mean(summary[3]) / n
    #         summary[4] = np.mean(summary[4]) / n
    #         summary[5] = np.mean(summary[5]) / n
    #         summary[6] = np.mean(summary[6]) / n
    #         summary[7] = np.mean(summary[7]) / n
    #         printed.write(",,,, ,, " + str(summary[0]) + ", " + str(summary[1]) + "," +
    #                       str(summary[2]) + ", " + str(summary[3]) + ", " + str(summary[4]) + ", " + str(summary[5]) +
    #                       ", " + str(summary[6]) + ", " + str(summary[7]) + "\n")
    #         printed.write("\n")
    #     printed.close()


    # def totaller(self):
    #     """
    #     TODO(Jesper): Jacob: What does this code do?
    #     :return:
    #     """
    #
    #     rankings = {}
    #     for exp in self._structured_datasets:
    #         name = exp.name.split('_')
    #         task = name[2]
    #         score = exp._metrics._motion[3]
    #         if task not in rankings:
    #             rankings[task] = {}
    #             rankings[task][score] = [exp]
    #         else:
    #             if score not in rankings[task]:
    #                 rankings[task][score] = [exp]
    #             else:
    #                 rankings[task][score].append(exp)
    #     return rankings
