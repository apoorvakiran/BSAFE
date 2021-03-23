"""
Computation tools including weighted average. Score scaling.

"""

import logging
import numpy as np
import math

logger = logging.getLogger()


def get_weighted_average(scores, bins=4, bin_weights=(2, 3, 4, 5), max_score=7):
    """
    Compute weighted average on safety scores. This way of computing average is
    a compromise between Maximum and Average.

    Higher risk scores will take more weight.
    """
    if bins <= 0 or int(bins) != bins:
        msg = "Number of bins should be positive integers!"
        logger.exception(msg)
        raise Exception(msg)

    if len(bin_weights) != bins:
        msg = "Number of bins should be equal to length of weights!"
        logger.exception(msg)
        raise Exception(msg)

    if len(scores) == 0:
        return 0

    bin_len = max_score / bins
    ranges = [(i * bin_len, (i + 1) * bin_len) for i in range(bins)]
    weighted_sum = 0
    scores_weights = []

    for score in scores:
        for range_, weight in zip(ranges, bin_weights):
            if (
                range_[0] <= score <= range_[1]
            ):  # This will cover all values from 0 to 7 inclusive
                weighted_sum += score * weight
                scores_weights.append(weight)
                break

    if sum(scores_weights) <= 0:
        return 0

    return weighted_sum / sum(scores_weights)


def scale_scores(scores):
    """
    Scale score up using a function.
    """
    if not (isinstance(scores, list) or isinstance(scores, np.ndarray)):
        msg = "Please pass in correct data type into scaling function!"
        logger.exception(msg)
        raise Exception(msg)

    else:
        if scores is None or scores[0] is None:
            return None
        elif len(scores) == 0:
            return None
        else:
            scores = np.array(scores)
            # Apply scaling function on all scores
            vectorized_func = np.vectorize(func_scaling)
            scaled_scores = vectorized_func(scores)
            return scaled_scores


def func_scaling(arr):
    # Scaling function:
    # 1. S shaped
    # 2. Pass (0,0), (7,7)
    # 3. ratio of scaled x to original x in the range of 0.9 to 1.5
    # 4. scale down score when score < 1; scale up score when score > 1
    # Parameters picked by fitting A/(B+exp(m*(x+n))) - C into system of equations
    if arr is not None:
        x_scaled = 7.477 / (0.9 + math.exp(-0.8 * (arr - 2.2))) - 1.114
        x_bounded_below = max(x_scaled, 0.0)
        x_bounded_above = min(x_bounded_below, 7.0)
        return x_bounded_above
    else:
        return None
