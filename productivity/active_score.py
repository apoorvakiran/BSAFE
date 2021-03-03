"""
Compute the proportion of actual moving time of wearable. This is also called active score.

@ author: Jessie Zhang
Copyright Iterate Labs 2018-
All Rights Reserved.
"""

import logging
import itertools
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

logger = logging.getLogger()


class ActiveScore(object):
    def __init__(self, raw_delta_values=None):
        """Construct ActiveScore object for the incoming data
        on Pitch, Roll, and Yaw delta values;

        Initialize two-level active scores to be None.
        """
        if raw_delta_values is not None:
            # If delta values received, check data format:
            data_entries = raw_delta_values.columns

            if not {"DeltaYaw", "DeltaPitch", "DeltaRoll"}.issubset(data_entries):
                msg = "Input data should have columns DeltaYaw, DeltaPitch, and DeltaRoll!"
                logger.exception(msg)
                raise Exception(msg)

            # Check date-time type
            assert (
                type(raw_delta_values.iloc[0]["Date-Time"]) == str
            ), "productivity metrics have wrong input data time type"

            raw_delta_values.sort_values(by="Date-Time", inplace=True, ascending=True)

            logger.info(
                f"{len(data_entries)} valid data points found for productivity metric"
            )

        self._raw_delta_values = raw_delta_values

    def compute_active_scores(
        self, intense_threshold=20, mild_threshold=10, plot=False
    ):
        """Compute two active scores using two sets of different thresholds.

        This is the main function of the class.
        """
        delta_values = self._raw_delta_values

        # None input for productivity metrics
        if delta_values is None:
            intense_active_score = None
            mild_active_score = None

        else:
            # Slide window through delta values to get data chunks,
            # and compute the absolute change inside each window
            diff_pitch = slide_window_get_chunk_diff(delta_values["DeltaPitch"])
            diff_roll = slide_window_get_chunk_diff(delta_values["DeltaRoll"])
            diff_yaw = slide_window_get_chunk_diff(delta_values["DeltaYaw"])

            logger.info("Looking for active time regions ...")

            # Find intense active points based on absolute change in windows
            # If at least two of dimensions have intense motion detected, mark as 'intense_activity'
            # active_points_found: np array of booleans
            intense_active_points_found = (
                (np.array(diff_pitch) > intense_threshold).astype(int)
                + (np.array(diff_roll) > intense_threshold).astype(int)
                + (np.array(diff_yaw) > intense_threshold).astype(int)
            ) > 1
            intense_activity_points = np.where(intense_active_points_found)[0]

            # Find mild active points based on absolute change in windows
            mild_active_points_found = (
                (np.array(diff_pitch) > mild_threshold).astype(int)
                + (np.array(diff_roll) > mild_threshold).astype(int)
                + (np.array(diff_yaw) > mild_threshold).astype(int)
            ) > 1
            mild_activity_points = np.where(mild_active_points_found)[0]

            start = 0
            end = len(diff_pitch)

            # Compute initial regions, remove short, merge close
            intense_regions = to_ranges(intense_activity_points)
            intense_regions_short_removed = remove_short_regions(intense_regions)
            intense_regions_close_merged = merge_close_regions(
                intense_regions_short_removed
            )

            mild_regions = to_ranges(mild_activity_points)
            mild_regions_short_removed = remove_short_regions(mild_regions)
            mild_regions_close_merged = merge_close_regions(mild_regions_short_removed)

            if plot:
                plt.figure(figsize=(100, 3))
                plt.plot(delta_values["DeltaPitch"].tolist(), label="Pitch")
                plt.plot(delta_values["DeltaRoll"].tolist(), label="Roll")
                plt.plot(delta_values["DeltaYaw"].tolist(), label="Yaw")
                # Show intense regions here
                for reg in intense_regions_close_merged:
                    plt.axvspan(reg[0], reg[1], color="r", alpha=0.1)
                plt.legend()
                plt.show()

            logger.info("Calculating Active Score ... ")

            intense_active_score = compute_regions_percentage(
                intense_regions_close_merged, start, end
            )
            mild_active_score = compute_regions_percentage(
                mild_regions_close_merged, start, end
            )

        active_score_report = {
            "intense_active_score": intense_active_score,
            "mild_active_score": mild_active_score,
        }

        return active_score_report


def to_ranges(list_of_points):
    """Convert list of points to a list of ranges represented as lists of lengths 2.

    For example, convert list of [1,2,3,7,8,9,10,100] to [[1,3],[7,10],[100,100]].
    """
    list_of_ranges = []
    for a, b in itertools.groupby(
        enumerate(list_of_points), lambda ab_pair: ab_pair[1] - ab_pair[0]
    ):
        b = list(b)
        list_of_ranges.append([b[0][1], b[-1][1]])
    return list_of_ranges


def slide_window_get_chunk_diff(data_list, time_chunk_len=10):
    """Slide window through data, cut data into chunks of length 10.
    Compute the maximum absolute difference of each chunk
    """
    chunks = []
    left_pointer = 0
    if len(data_list) == 0:
        return chunks
    if len(data_list) < time_chunk_len:
        chunks.append(data_list[left_pointer : left_pointer + len(data_list)])
    else:
        while left_pointer + time_chunk_len < len(data_list):
            chunks.append(data_list[left_pointer : left_pointer + time_chunk_len])
            left_pointer += 1
    diff_of_chunks = [max(chunk) - min(chunk) for chunk in chunks]
    return diff_of_chunks


def remove_short_regions(raw_regions, maximum_length=15):
    """Remove regions whose lengths are shorter than threshold.
    """
    index = 0
    index_to_remove = []
    while index < len(raw_regions):
        if raw_regions[index][1] - raw_regions[index][0] < maximum_length:
            index_to_remove.append(index)
        index += 1
    index_to_remove = index_to_remove[::-1]
    # Construct new list of regions
    new_regions = raw_regions.copy()
    for i in index_to_remove:
        new_regions.remove(new_regions[i])
    return new_regions


def merge_close_regions(list_of_regions, minimum_distance=15):
    """Merge exclusive regions whose distance between each other is smaller than threshold.

    In real cases, this method merges two time ranges which are close (being apart less than
    1.5 second in default settings) to each other.
    """
    new_regions = []
    # merge_indicator will be changed to 1 if any pair of close regions found
    merge_indicator = 0

    i = 0
    while i < len(list_of_regions):
        # There are at least two regions remaining:
        if i + 1 < len(list_of_regions):
            # Found close regions
            if (
                abs(list_of_regions[i][1] - list_of_regions[i + 1][0])
                < minimum_distance
            ):
                # Merge, and append to new list
                new_regions.append([list_of_regions[i][0], list_of_regions[i + 1][1]])
                i += 2
                merge_indicator = 1
            # No close regions found
            else:
                # Append to new list directly
                new_regions.append(list_of_regions[i])
                i += 1
        # There is only one region remained to check
        else:
            # Append directly
            new_regions.append(list_of_regions[i])
            i += 1

    # The list has been modified at least once, we need to iterate all regions again
    if merge_indicator != 0:
        return merge_close_regions(new_regions)
    # No close region has been detected, no need to go through again
    elif merge_indicator == 0:
        return new_regions


def compute_regions_percentage(regions, start, end):
    """compute the proportion of the regions being covered over the total time length
    """
    shadowed = 0
    for r in regions:
        shadowed += r[1] - r[0]
    if (end - start) > 0:
        return shadowed / (end - start)
    else:
        return 0
