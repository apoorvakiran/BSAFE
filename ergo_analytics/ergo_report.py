# -*- coding: utf-8 -*-
"""Handles reporting of Ergonomic Metrics and results.

@ author Jesper Kristensen
Copyright Iterate Labs 2018-
All Rights Reserved.
"""

import logging
from datetime import datetime
import json
import numpy as np
import pandas as pd
from recommendations import recommend

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

    def to_http(
        self,
        api_client=None,
        combine_across_time="max",
        combine_across_parameter="average",
        mac_address=None,
        just_return_payload=False,
        run_as_test=False,
        **kwargs
    ):
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

        payload = self._construct_payload(
            combine_across_parameter=combine_across_parameter,
            combine_across_time=combine_across_time,
        )

        if just_return_payload:
            logger.debug(
                "Just returning the payload from to_http (not sending to endpoint!)."
            )
            return payload

        # put information about device in the payload:
        payload["mac"] = mac_address
        try:
            logger.info("Sending payload to endpoint /api/v1/safety_scores")
            if not run_as_test:
                # not a test - so post the request
                self._response = api_client.post_request(
                    "api/v1/safety_scores", payload
                )
                logger.info("response is = {}".format(self._response))
                logger.info(self._response.text)
                self._response.raise_for_status()
            else:
                logger.debug(
                    "Running in test mode so NOT posting safety scores to API!"
                )

        except Exception:
            logger.error("Failure to send request", exc_info=True)

        logger.debug("Success - report with safety scores sent!")

    def _construct_payload(
        self, combine_across_parameter="average", combine_across_time="max"
    ):
        """Construct the payload to report out.

        :return: dict representing the payload.
        """
        ergo_metrics = self._ergo_metrics
        # Compute safety scores
        get_score = ergo_metrics.get_score
        # Compute productivity scores
        get_active_score = ergo_metrics.get_active_scores
        get_peak_analysis = ergo_metrics.get_peak_analysis

        payload_dict = dict()

        start_time = ergo_metrics.earliest_time
        end_time = ergo_metrics.latest_time

        # get speed and posture scores as a whole:
        # speed and posture are both with format:
        # [[yaw1, pitch1, roll1],
        #  [yaw2, pitch2, roll2],
        #  ... ...
        #  [yawN, pitchN, rollN]]

        speed = get_score(
            name="AngularActivityScore",
            combine_across_parameter=combine_across_parameter,
        )
        posture = get_score(
            name="PostureScore", combine_across_parameter=combine_across_parameter
        )

        active_report = get_active_score()
        peak_analysis = get_peak_analysis()

        logger.info(f"Active report generated: {active_report}")
        logger.info(f"Peak Analysis results generated: {peak_analysis}")

        speed = pd.DataFrame(np.vstack(speed)).dropna(how="any")
        posture = pd.DataFrame(np.vstack(posture)).dropna(how="any")

        # extract lists of safety scores, speed scores, and posture scores
        # safety scores are defined as speed_pitch
        # speed_score and posture_score take the maximum of
        # [yaw_n, pitch_n, roll_n] for each n from 1 to N
        speed_pitch_all = speed.loc[:, 1].tolist()
        speed_score_all = speed.max(axis=1).tolist()
        posture_score_all = posture.max(axis=1).tolist()

        all_scores_dic = {
            "safety_score": speed_pitch_all,
            "speed_score": speed_score_all,
            "posture_score": posture_score_all,
        }

        # get avg_safety_score by averaging all speed_pitch across time
        avg_safety_score = np.mean(speed_pitch_all)
        safety_score_vs_time = "_".join([str(score) for score in speed_pitch_all])

        # Default num_bin = 3
        # num_bins = 3
        #
        # bins_weights = [
        #     sum(i*7/num_bins < score <= (i+1)*7/num_bins
        #         for score in speed_pitch_all)/len(speed_pitch_all)
        #     for i in range(num_bins)
        # ]
        #
        # weighted_scores = \
        #     sum([bins_weights[i] * np.mean([i*7/num_bins, (i+1)*7/num_bins])
        #          for i in range(num_bins)])
        weighted_scores = 0

        if combine_across_time == "max":
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
            first_data_times = self._ergo_metrics.get_first_time(
                chunk_index=0, as_string=True
            )
            last_data_times = self._ergo_metrics.get_last_time(
                chunk_index=-1, as_string=True
            )

        elif combine_across_time == "keep-separate":

            speed_yaw = speed.iloc[:, 0].tolist()
            speed_pitch = speed.iloc[:, 1].tolist()
            speed_roll = speed.iloc[:, 2].tolist()

            posture_yaw = posture.iloc[:, 0].tolist()
            posture_pitch = posture.iloc[:, 1].tolist()
            posture_roll = posture.iloc[:, 2].tolist()

            speed_score = np.max(speed, axis=1).tolist()
            posture_score = np.max(posture, axis=1).tolist()

            # in this case, we have the score vs time, so create the list of indices:
            from_times = []
            till_times = []
            for chunk_index in range(ergo_metrics.number_of_data_chunks):
                this_first_time = self._ergo_metrics.get_first_time(
                    chunk_index=chunk_index, as_string=True
                )
                this_last_time = self._ergo_metrics.get_last_time(
                    chunk_index=chunk_index, as_string=True
                )

                from_times.append(this_first_time)
                till_times.append(this_last_time)

            first_data_times = from_times
            last_data_times = till_times
        else:
            raise NotImplementedError("Implement me!")

        payload_dict["speed_pitch_score"] = speed_pitch
        payload_dict["speed_yaw_score"] = speed_yaw
        payload_dict["speed_roll_score"] = speed_roll

        payload_dict["normalized_speed_pitch_score"] = speed_pitch
        payload_dict["normalized_speed_yaw_score"] = speed_yaw
        payload_dict["normalized_speed_roll_score"] = speed_roll
        payload_dict["speed_score"] = speed_score
        #
        payload_dict["posture_pitch_score"] = posture_pitch
        payload_dict["posture_yaw_score"] = posture_yaw
        payload_dict["posture_roll_score"] = posture_roll
        payload_dict["posture_score"] = posture_score
        #
        payload_dict["safety_score"] = speed_pitch

        # Add productivity metrics: active scores to payload_dic
        payload_dict["intense_active_score"] = active_report["intense_active_score"]
        payload_dict["mild_active_score"] = active_report["mild_active_score"]
        payload_dict["total_time_in_sec"] = active_report["total_time_in_sec"]
        payload_dict["intense_active_time_in_sec"] = active_report["intense_active_time_in_sec"]
        payload_dict["mild_active_time_in_sec"] = active_report["mild_active_time_in_sec"]

        # recommendation id
        rec = recommend.Recommendation(
            all_scores_dic, recommend.default_rec_dic, recommend.default_threshold_dic
        )
        payload_dict["recommendation_id"] = rec.rec_top_priority()

        # avg safety score
        payload_dict["safety_score_average"] = avg_safety_score
        # safety score v.s. time
        payload_dict["safety_score_vs_time"] = safety_score_vs_time
        # weighted safety score
        payload_dict["weighted_safety_score_average"] = weighted_scores

        if not combine_across_time == "keep-separate":
            # not covered yet with "keep separate":
            payload_dict["strain_pitch_score"] = max(
                0, posture_pitch - np.random.uniform(0, 1)
            )
            payload_dict["strain_yaw_score"] = max(
                0, posture_yaw - np.random.uniform(0, 1)
            )
            payload_dict["strain_roll_score"] = max(
                0, posture_roll - np.random.uniform(0, 1)
            )
            payload_dict["strain_score"] = np.max(posture)

        payload_dict["start_time"] = str(start_time)
        payload_dict["end_time"] = str(end_time)

        # when was this run?
        analyzed_at_time = datetime.now().utcnow().isoformat()
        payload_dict["analyzed_at"] = str(analyzed_at_time)

        payload_dict["first_data_times"] = first_data_times
        payload_dict["last_data_times"] = last_data_times

        logger.info("Payload dict = {}".format(payload_dict))

        return payload_dict

    def to_csv(self):
        """Report out to CSV."""
        msg = "to_csv() method not implemented - implement me!"
        logger.exception(msg)
        raise NotImplementedError(msg)

    def to_json(self, combine_across_parameter="average", combine_across_time="max"):
        """Report out in a JSON format."""
        payload_json = self._construct_payload(
            combine_across_parameter=combine_across_parameter,
            combine_across_time=combine_across_time,
        )
        self._response = "success"
        return payload_json

    def to_string(self, combine_across_parameter="average"):
        """Report out as a string."""
        payload = self._construct_payload(
            combine_across_parameter=combine_across_parameter
        )
        self._response = "success"
        return json.dumps(payload)
