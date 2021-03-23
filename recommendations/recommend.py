# payload_dict["speed_pitch_score"] = speed_pitch
# payload_dict["speed_yaw_score"] = speed_yaw
# payload_dict["speed_roll_score"] = speed_roll
#
# payload_dict["normalized_speed_pitch_score"] = speed_pitch
# payload_dict["normalized_speed_yaw_score"] = speed_yaw
# payload_dict["normalized_speed_roll_score"] = speed_roll
# payload_dict["speed_score"] = speed_score
# #
# payload_dict["posture_pitch_score"] = posture_pitch
# payload_dict["posture_yaw_score"] = posture_yaw
# payload_dict["posture_roll_score"] = posture_roll
# payload_dict["posture_score"] = posture_score
# #
# payload_dict["safety_score"] = speed_pitch

default_rec_dic = {
    1: "time-dependent safety_score has spent more than 50% time over 4",
    2: "time-dependent speed_score has spent 50% time over 4",
    3: "time_dependent posture_score has spent 50% time over 4",
    4: "time-dependent safety_score has spent 50% time over 3",
    5: "time-dependent speed_score has spent 50% time over 3",
    6: "time_dependent posture_score has spent 50% time over 3",
}

default_threshold_dic = {
    1: ["safety_score", 0.5, 4],
    2: ["speed_score", 0.5, 4],
    3: ["posture_score", 0.5, 4],
    4: ["safety_score", 0.5, 3],
    5: ["speed_score", 0.5, 3],
    6: ["posture_score", 0.5, 3],
}


class Recommendation(object):
    def __init__(self, payload_dict, rec_dic=None, threshold_dic=None):
        """
            @type rec_dic: dict[int,str]
            @type threshold_dic: dict[int,list[object]]
        """
        # rec_dic: dict[int,str]
        # threshold_dic: dict[int,list[object]]
        self._payload_dict = payload_dict
        self._num_rec = len(rec_dic)
        self._rec_dic = rec_dic
        self._threshold_dic = threshold_dic

    def recommendation(self, rec_id_to_check):
        """
        Return boolean value to indicate whether to give recommendation 1
        """
        threshold_dic = self._threshold_dic

        if not (1 <= rec_id_to_check <= len(threshold_dic)):
            raise Exception(
                "rec_id out of range" "Choose rec_id in between", 1, len(threshold_dic)
            )

        else:
            score_to_evaluate = threshold_dic[rec_id_to_check][0]
            duration_limit = threshold_dic[rec_id_to_check][1]
            score_top_limit = threshold_dic[rec_id_to_check][2]

            if (
                score_to_evaluate in {"safety_score", "speed_score", "posture_score"}
                and 0 <= score_top_limit <= 4.5
                and 0 <= duration_limit <= 1
            ):

                # Get scores to be evaluated
                scores = self._payload_dict[score_to_evaluate]

                # Find threshold percentile of score
                if not isinstance(scores, float):
                    if scores is None:
                        duration_unsafe = 0
                    elif len(scores) == 0:
                        duration_unsafe = 0
                    elif len(scores) > 0:
                        cnt = 0
                        for score in scores:
                            if score >= score_top_limit:
                                cnt += 1
                        duration_unsafe = cnt / len(scores)
                else:
                    duration_unsafe = 1 if scores > score_top_limit else 0

                # Check whether
                if duration_unsafe >= duration_limit:
                    return True
                else:
                    return False

            else:
                if score_to_evaluate not in {
                    "safety_score",
                    "speed_score",
                    "posture_score",
                }:
                    raise Exception(
                        "score_to_evaluate should be one among",
                        "safety_score, speed_score, and posture_score",
                    )
                elif not (0 <= score_top_limit <= 4.5):
                    raise Exception(
                        "score_top_limit out of range ",
                        "Choose a number in between 0 and 4.5",
                    )
                elif not (0 <= duration_limit <= 1):
                    raise Exception(
                        "duration_limit out of range ",
                        "Choose a number in between 0 and 1",
                    )

    @property
    def recommendation_lattice(self):
        """
        Mapping all recommendations to a priority ranking
        """
        rec_dic = self._rec_dic

        # Initialize rec_lattice
        rec_lattice = {i: False for i in range(1, len(rec_dic) + 1)}

        # Check each recommendation in rec_dic
        # If True, change value in rec_lattice
        for i in range(1, len(rec_dic) + 1):
            rec_lattice[i] = self.recommendation(i)

        return rec_lattice

    def rec_top_priority(self):
        """
        Find the most important recommendation based on built-in priority
        """
        rec_lattice = self.recommendation_lattice

        for rec_id in rec_lattice:
            if rec_lattice[rec_id] is True:
                return rec_id
        return None

    def rec_lattice(self):
        pass
