"""
Computation tools including weighted average. Score scaling.

"""

import logging

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
        msg = "Number of bins should be equal to lenghth of weights!"
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
            if range_[0] <= score < range_[1]:
                weighted_sum += score * weight
                scores_weights.append(weight)

    if sum(scores_weights) <= 0:
        return 0

    return weighted_sum / sum(scores_weights)
