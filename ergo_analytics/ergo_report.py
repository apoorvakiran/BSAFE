# -*- coding: utf-8 -*-
"""Handles reporting of Ergonomic Metrics and results.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
All Rights Reserved.
"""

import logging
from datetime import datetime
import requests

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

    def to_http(self, endpoint=None, authorization=None,
                combine_across_data_chunks='average', mac_address=None):
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

        payload = self._construct_payload(combine_across_data_chunks=combine_across_data_chunks)

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

    def _construct_payload(self, combine_across_data_chunks='average'):
        """Constructs the payload to report out.

        :return: dict representing the payload.
        """

        ergo_metrics = self._ergo_metrics

        payload_dict = dict()

        # which metrics do we have?
        for metric_name in ergo_metrics.metrics:
            payload_dict[metric_name] = \
                ergo_metrics.get_score(name=metric_name,
                                       combine_across_data_chunks=combine_across_data_chunks)

        start_time = ergo_metrics.earliest_time
        end_time = ergo_metrics.latest_time
        payload_dict['start_time'] = str(start_time)
        payload_dict['end_time'] = str(end_time)

        analyzed_at_time = datetime.now().utcnow().isoformat()
        payload_dict['analyzed_at'] = str(analyzed_at_time)

        logger.info("Payload dict = {}".format(payload_dict))

        return payload_dict

    def to_csv(self):
        """Report out to CSV."""
        msg = "to_csv() method not implemented - implement me!"
        logger.exception(msg)
        raise NotImplementedError(msg)

    def to_json(self, combine_across_data_chunks='average'):
        """Report out in a JSON format."""
        payload_json = self._construct_payload(combine_across_data_chunks=combine_across_data_chunks)
        self._response = 'success'
        return payload_json

    def to_string(self, combine_across_data_chunks='average'):
        """Report out as a string."""
        payload = self._construct_payload(combine_across_data_chunks=combine_across_data_chunks)
        self._response = 'success'
        return payload
