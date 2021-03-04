"""
Compute several metrics on peak and cycle analysis. This gives us information on
motion frequency.

@ author: Jessie Zhang
Copyright Iterate Labs 2018-
All Rights Reserved.
"""
import logging
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger()

# find_peaks function has height, threshold, distance, prominence,
# and width etc. as parameters. In this dictionary, we store three sets
# of those parameters to look for different types of peaks in motion data.
default_peak_parameters = {
    "high_peak": {
        "height": None,
        "prominence": 60,
        "threshold": None,
        "distance": 10,
        "width": 10,
    },
    "medium_peak": {
        "height": None,
        "prominence": 40,
        "threshold": None,
        "distance": 10,
        "width": 10,
    },
    "low_peak": {
        "height": None,
        "prominence": 20,
        "threshold": None,
        "distance": 5,
        "width": 5,
    },
}


class PeakAnalyzer(object):
    def __init__(self, raw_delta_values):
        """Construct PeakAnalyzer object for the incoming data
                on Pitch, Roll, and Yaw delta values.

                The number of peaks implies the frequency
                """
        if raw_delta_values is not None:
            # If delta values received, check data format:
            data_entries = raw_delta_values.columns

            if not {"DeltaYaw", "DeltaPitch", "DeltaRoll"}.issubset(data_entries):
                msg = "Input data should have columns DeltaYaw, DeltaPitch, and DeltaRoll!"
                logger.exception(msg)
                raise Exception(msg)

            assert (
                type(raw_delta_values.iloc[0]["Date-Time"]) == pd.Timestamp
                or type(raw_delta_values.iloc[0]["Date-Time"]) == str
            ), "productivity metrics have wrong input data time type"

            raw_delta_values.sort_values(by="Date-Time", inplace=True, ascending=True)

        self._raw_delta_values = raw_delta_values
        self._peak_parameters_dic = default_peak_parameters

    # Jessie: Apply filter to solve moving average problem
    def solve_moving_average(self):
        """Add a filter to solve moving average problem"""
        pass

    def find_all_peaks(
        self, peak_type, on_column="DeltaPitch", simple_scale=False, plot=False
    ):
        """Look for motion signal peaks in given data.
        """
        if peak_type not in self._peak_parameters_dic.keys():
            msg = "Please pass in a valid peak_type or change parameter dic!"
            logger.exception(msg)
            raise Exception(msg)

        # delta_pitch = self._raw_delta_values["DeltaPitch"]
        # delta_roll = self._raw_delta_values["DeltaRoll"]
        # delta_yaw = self._raw_delta_values["DeltaYaw"]

        arr_to_find_peaks = self._raw_delta_values[on_column]

        # Simple scaling makes the data to have mean value of zero
        # Usually we do not use it b/c find_peaks function has default height to be None
        if simple_scale:
            mean = np.mean(arr_to_find_peaks)
            arr_to_find_peaks = arr_to_find_peaks - mean

        # Find peaks indices by signal.find_peaks
        peaks, _ = find_peaks(
            arr_to_find_peaks,
            height=self._peak_parameters_dic[peak_type]["height"],
            prominence=self._peak_parameters_dic[peak_type]["prominence"],
            width=self._peak_parameters_dic[peak_type]["width"],
            distance=self._peak_parameters_dic[peak_type]["distance"],
            threshold=self._peak_parameters_dic[peak_type]["threshold"],
        )
        if plot:
            plt.figure(figsize=(100, 3))
            plt.plot(arr_to_find_peaks)
            plt.plot(peaks, arr_to_find_peaks[peaks], "x")
            plt.plot(np.zeros_like(arr_to_find_peaks), "--", color="gray")
            plt.show()

        return peaks

    def generate_peak_report(self):
        """Find number of peaks in different types.
        Return a dictionary which stores the numbers of each type.
        """
        # all peak types
        all_types_ = self._peak_parameters_dic.keys()
        # If no data found, return dictionary will None values
        if self._raw_delta_values is None:
            return {peak_type_: 0 for peak_type_ in all_types_}
        else:
            # construct a dictionary of type name to the number of peaks detected
            peak_report = {
                peak_type_: len(self.find_all_peaks(peak_type_))
                for peak_type_ in all_types_
            }
            return peak_report

    def update_parameter_dic(self, new_parameter_dic):
        """update parameter dictionary
        """
        self._peak_parameters_dic = new_parameter_dic

    @property
    def peak_parameters_dic(self):
        return self._peak_parameters_dic
