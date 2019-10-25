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

    _ergo_metrics = None
    _mac_address = None
    _response = None

    def __init__(self, ergo_metrics=None, mac_address=None):
        """
        Create an ErgoReport object with ability to report out the ergo
        metrics and other information.
        :param report_out_via:
        :param ergo_metrics:
        :param authorization:
        :param destination:
        :param mac_address:
        """

        self._ergo_metrics = ergo_metrics
        self._mac_address = mac_address

    @property
    def response(self):
        """
        Stores information about any results from reporting out.
        For example, if sending to an HTTP endpoint: what is the return code?
        :return:
        """
        return self._response

    def to_http(self, endpoint=None, authorization=None):
        """
        Reports out to an HTTP endpoint.
        :param endpoint:
        :param authorization:
        :return:
        """
        payload = self._construct_payload()
        try:
            headers = {'Authorization': authorization}
            self._response = \
                requests.post(endpoint, headers=headers, data=payload)
            self._response.raise_for_status()
        except Exception:
            logger.error("Failure to send request", exc_info=True)

    def _construct_payload(self):
        """
        Constructs the payload to send to the HTTP endpoint.
        :return:
        """

        get_score = self._ergo_metrics.get_score

        payload_dict = dict()
        payload_dict['mac'] = self._mac_address
        #
        payload_dict['speed_pitch_score'] = get_score('speed/pitch')
        payload_dict['speed_yaw_score'] = get_score('speed/yaw')
        payload_dict['speed_roll_score'] = get_score('speed/roll')

        payload_dict['normalized_speed_pitch_score'] = \
            get_score('speed/pitch_normalized')
        payload_dict['normalized_speed_yaw_score'] = \
            get_score('speed/yaw_normalized')
        payload_dict['normalized_speed_roll_score'] = \
            get_score('speed/roll_normalized')
        payload_dict['speed_score'] = get_score('speed/total')
        #
        payload_dict['strain_pitch_score'] = get_score('strain/pitch')
        payload_dict['strain_yaw_score'] = get_score('strain/yaw')
        payload_dict['strain_roll_score'] = get_score('strain/roll')
        payload_dict['strain_score'] = get_score('strain/total')
        #
        payload_dict['posture_pitch_score'] = get_score('posture/pitch')
        payload_dict['posture_yaw_score'] = get_score('posture/yaw')
        payload_dict['posture_roll_score'] = get_score('posture/roll')
        payload_dict['posture_score'] = get_score('posture/unsafe')
        #
        payload_dict['safety_score'] = get_score('total')

        time = self._ergo_metrics.data.time

        start_time = time.iloc[0]
        end_time = time.iloc[-1]
        payload_dict['start_time'] = start_time
        payload_dict['end_time'] = end_time

        analyzed_at_time = datetime.now().utcnow().isoformat()
        payload_dict['analyzed_at'] = analyzed_at_time

        return payload_dict

    def to_csv(self):
        raise NotImplementedError("Implement me!")

    def to_string(self):
        payload = self._construct_payload()
        return payload

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
