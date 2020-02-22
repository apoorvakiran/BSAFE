# -*- coding: utf-8 -*-
"""Handles reporting of Ergonomic Metrics and results.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
All Rights Reserved.
"""

import logging
from datetime import datetime
import json
import requests
import numpy as np
import pandas as pd

__all__ = ["ErgoReport"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class ErgoReport(object):
    """Given an ErgoMetrics object receive the scoring output in your
    preferred format: csv, HTTP, string, etc.

    Standardize the report-out.
    """

    _ergo_metrics = None
    _response = None

    def __init__(self, ergo_metrics=None):
        """
        Create an ErgoReport object with ability to report out the ergo
        metrics and other information.

        :param report_out_via:
        :param ergo_metrics:
        :param authorization:
        :param destination:
        """
        self._ergo_metrics = ergo_metrics

    @property
    def response(self):
        """Stores information about any results from reporting out.
        For example, if sending to an HTTP endpoint: what is the return code?
        :return:
        """
        return self._response

    def to_http(self, endpoint=None, authorization=None, combine_across_time='max',
                combine_across_parameter='average', mac_address=None, just_return_payload=False):
        """Reports out to an HTTP endpoint.

        Side effect: the response from POST to the end point of this
        report-out is the response attribute.

        :param endpoint:
        :param authorization:
        :param mac_address: what mac address is this device?
        :param combine_across_data_chunks: How to combine the score over
        multiple data chunks?

        :return: Nothing, side effect is to set the response variable.
        """

        payload = self._construct_payload(combine_across_parameter=combine_across_parameter,
                                          combine_across_time=combine_across_time)

        if just_return_payload:
            logger.debug("Just returning the payload from to_http (not sending to endpoint!).")
            return payload

        # put information about device in the payload:
        payload['mac'] = mac_address
        try:
            headers = {'Authorization': authorization}
            logger.info("Sending payload to endpoint {}".format(endpoint))
            self._response = \
                requests.post(endpoint, headers=headers, data=payload)
            logger.info("response is = {}".format(self._response))
            logger.info(self._response.text)

            self._response.raise_for_status()
        except Exception:
            logger.error("Failure to send request", exc_info=True)

    def _construct_payload(self, combine_across_parameter='average',
                           combine_across_time='max'):
        """Constructs the payload to report out.

        :return: dict representing the payload.
        """

        ergo_metrics = self._ergo_metrics
        get_score = ergo_metrics.get_score

        payload_dict = dict()

        start_time = ergo_metrics.earliest_time
        end_time = ergo_metrics.latest_time

        # # which metrics do we have?
        # for metric_name in ergo_metrics.metrics:
        #     payload_dict[metric_name] = \
        #         ergo_metrics.get_score(name=metric_name,
        #                                combine_across_data_chunks=combine_across_data_chunks)

        speed = get_score(name='activity', combine_across_parameter=combine_across_parameter)
        posture = get_score(name='posture', combine_across_parameter=combine_across_parameter)

        speed = pd.DataFrame(np.vstack(speed)).dropna(how='any')
        posture = pd.DataFrame(np.vstack(posture)).dropna(how='any')
        if combine_across_time == 'max':
            # take max score across time:
            speed = speed.max(axis=0).tolist()
            speed_yaw, speed_pitch, speed_roll = speed

            posture = posture.max(axis=0).tolist()
            posture_yaw, posture_pitch, posture_roll = posture

            speed_score = np.max(speed)
            posture_score = np.max(posture)

            # in this case, the score is the max over all chunks
            # we the first and last index is the very first data index and
            # the last index is the very last index:
            first_data_index = self._ergo_metrics.get_first_data_index(chunk_index=0)
            last_data_index = self._ergo_metrics.get_last_data_index(chunk_index=-1)

        elif combine_across_time == 'keep-separate':

            speed_yaw = speed.iloc[:, 0].tolist()
            speed_pitch = speed.iloc[:, 1].tolist()
            speed_roll = speed.iloc[:, 2].tolist()

            posture_yaw = posture.iloc[:, 0].tolist()
            posture_pitch = posture.iloc[:, 1].tolist()
            posture_roll = posture.iloc[:, 2].tolist()

            speed_score = np.max(speed, axis=0).tolist()
            posture_score = np.max(posture, axis=0).tolist()

            # in this case, we have the score vs time, so create the list of indices:
            from_indices = []
            till_indices = []
            for chunk_index in range(ergo_metrics.number_of_data_chunks):
                this_first_data_index = self._ergo_metrics.get_first_data_index(chunk_index=chunk_index)
                this_last_data_index = self._ergo_metrics.get_last_data_index(chunk_index=chunk_index)

                from_indices.append(this_first_data_index)
                till_indices.append(this_last_data_index)
            first_data_index = from_indices
            last_data_index = till_indices
        else:
            raise NotImplementedError("Implement me!")

        payload_dict['speed_pitch_score'] = speed_pitch
        payload_dict['speed_yaw_score'] = speed_yaw
        payload_dict['speed_roll_score'] = speed_roll

        payload_dict['normalized_speed_pitch_score'] = speed_pitch
        payload_dict['normalized_speed_yaw_score'] = speed_yaw
        payload_dict['normalized_speed_roll_score'] = speed_roll
        payload_dict['speed_score'] = speed_score
        #
        payload_dict['posture_pitch_score'] = posture_pitch
        payload_dict['posture_yaw_score'] = posture_yaw
        payload_dict['posture_roll_score'] = posture_roll
        payload_dict['posture_score'] = posture_score
        #
        payload_dict['safety_score'] = speed_pitch

        if not combine_across_time == 'keep-separate':
            # not covered yet with "keep separate":
            payload_dict['strain_pitch_score'] = max(0, posture_pitch - np.random.uniform(0, 1))
            payload_dict['strain_yaw_score'] = max(0, posture_yaw - np.random.uniform(0, 1))
            payload_dict['strain_roll_score'] = max(0, posture_roll - np.random.uniform(0, 1))
            payload_dict['strain_score'] = np.max(posture)

        payload_dict['start_time'] = str(start_time)
        payload_dict['end_time'] = str(end_time)

        # when was this run?
        analyzed_at_time = datetime.now().utcnow().isoformat()
        payload_dict['analyzed_at'] = str(analyzed_at_time)

        payload_dict['first_data_index'] = first_data_index
        payload_dict['last_data_index'] = last_data_index

        logger.info("Payload dict = {}".format(payload_dict))

        return payload_dict

    def to_csv(self):
        """Report out to CSV."""
        msg = "to_csv() method not implemented - implement me!"
        logger.exception(msg)
        raise NotImplementedError(msg)

    def to_json(self, combine_across_parameter='average', combine_across_time='max'):
        """Report out in a JSON format."""
        payload_json = self._construct_payload(combine_across_parameter=combine_across_parameter,
                                               combine_across_time=combine_across_time)
        self._response = 'success'
        return payload_json

    def to_string(self, combine_across_parameter='average'):
        """Report out as a string."""
        payload = self._construct_payload(combine_across_parameter=combine_across_parameter)
        self._response = 'success'
        return json.dumps(payload)
