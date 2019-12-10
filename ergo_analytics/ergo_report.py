# -*- coding: utf-8 -*-
"""
Handles reporting of Ergonomic Metrics and results to customers / the caller.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
"""

import logging
from datetime import datetime
import requests

__all__ = ["ErgoReport"]
__author__ = "Iterate Labs, Inc."
__version__ = "Alpha"

logger = logging.getLogger()


class ErgoReport(object):
    """
    Provide an ErgoMetrics object and receive the output however you want:
    CSV, HTTP, String, etc.
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
        """
        Stores information about any results from reporting out.
        For example, if sending to an HTTP endpoint: what is the return code?
        :return:
        """
        return self._response

    def to_http(self, endpoint=None, authorization=None,
                combine_across_data_chunks='average', mac_address=None):
        """
        Reports out to an HTTP endpoint.

        Stores the response in self.response.

        :param endpoint:
        :param authorization:
        :param mac_address: what mac address is this device?
        :param combine_across_data_chunks: How to combine the score over
        multiple data chunks?

        :return: Nothing, side effect is to set the response variable.
        """

        payload = self._construct_payload(combine=combine_across_data_chunks)

        # put information about device in the payload:
        payload['mac'] = mac_address
        try:
            headers = {'Authorization': authorization}
            self._response = \
                requests.post(endpoint, headers=headers, data=payload)
            self._response.raise_for_status()
        except Exception:
            logger.error("Failure to send request", exc_info=True)

    def _construct_payload(self, combine='average'):
        """
        Report to HTTP.
        Constructs the payload to send to the HTTP endpoint.

        :return: dict representing the payload.
        """

        get_score = self._ergo_metrics.get_score

        payload_dict = dict()
        #
        payload_dict['speed_pitch_score'] = get_score(name='speed/pitch',
                                                      combine=combine)
        payload_dict['speed_yaw_score'] = get_score(name='speed/yaw',
                                                    combine=combine)
        payload_dict['speed_roll_score'] = get_score(name='speed/roll',
                                                     combine=combine)

        payload_dict['normalized_speed_pitch_score'] = \
            get_score(name='speed/pitch_normalized', combine=combine)
        payload_dict['normalized_speed_yaw_score'] = \
            get_score(name='speed/yaw_normalized', combine=combine)
        payload_dict['normalized_speed_roll_score'] = \
            get_score(name='speed/roll_normalized', combine=combine)
        payload_dict['speed_score'] = get_score(name='speed/total',
                                                combine=combine)
        #
        payload_dict['strain_pitch_score'] = get_score(name='strain/pitch',
                                                       combine=combine)
        payload_dict['strain_yaw_score'] = get_score(name='strain/yaw',
                                                     combine=combine)
        payload_dict['strain_roll_score'] = get_score(name='strain/roll',
                                                      combine=combine)
        payload_dict['strain_score'] = get_score(name='strain/total',
                                                 combine=combine)
        #
        payload_dict['posture_pitch_score'] = get_score(name='posture/pitch',
                                                        combine=combine)
        payload_dict['posture_yaw_score'] = get_score(name='posture/yaw',
                                                      combine=combine)
        payload_dict['posture_roll_score'] = get_score(name='posture/roll',
                                                       combine=combine)
        payload_dict['posture_score'] = get_score(name='posture/unsafe',
                                                  combine=combine)
        #
        payload_dict['safety_score'] = get_score(name='total',
                                                 combine=combine)

        start_time = self._ergo_metrics.earliest_time
        end_time = self._ergo_metrics.latest_time
        payload_dict['start_time'] = start_time
        payload_dict['end_time'] = end_time

        analyzed_at_time = datetime.now().utcnow().isoformat()
        payload_dict['analyzed_at'] = analyzed_at_time

        logger.debug(payload_dict)

        return payload_dict

    def to_csv(self):
        """
        Report to CSV.
        """
        msg = "to_csv() method not implemented - implement me!"
        logger.exception(msg)
        raise NotImplementedError(msg)

    def to_string(self, combine_across_data_chunks='average'):
        """
        Report to string.
        """
        payload = self._construct_payload(combine=combine_across_data_chunks)
        self._response = 'success'
        return payload
