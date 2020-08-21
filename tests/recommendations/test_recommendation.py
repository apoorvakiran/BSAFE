from recommendations import recommend
import unittest
class TestRecommendation(unittest.TestCase):
    def test_recommendation(self):
        payload_dict1 = dict(
            safety_score=[3.1, 4.1, 4.1],
            speed_score=[3.1, 3.1, 4.1],
            posture_score=[2.1, 2.1, 5.1]
        )
        rec = recommend.Recommendation(
            payload_dict=payload_dict1,
            rec_dic=recommend.default_rec_dic,
            threshold_dic=recommend.default_threshold_dic
        )
        self.assertTrue(rec.recommendation(1))
        self.assertFalse(rec.recommendation(2))
        self.assertFalse(rec.recommendation(3))
        self.assertTrue(rec.recommendation(4))
        self.assertTrue(rec.recommendation(5))
        self.assertFalse(rec.recommendation(6))
    def test_recommendation2(self):
        payload_dict2 = dict(
            safety_score=[3.1, 3.1, 4.1],
            speed_score=[4.1, 4.1, 4.1],
            posture_score=[3.1, 3.1, 5.1]
        )
        rec = recommend.Recommendation(
            payload_dict=payload_dict2,
            rec_dic=recommend.default_rec_dic,
            threshold_dic=recommend.default_threshold_dic
        )
        self.assertFalse(rec.recommendation(1))
        self.assertTrue(rec.recommendation(2))
        self.assertFalse(rec.recommendation(3))
        self.assertTrue(rec.recommendation(4))
        self.assertTrue(rec.recommendation(5))
        self.assertTrue(rec.recommendation(6))
    def test_recommendation_lattice(self):
        payload_dict1 = dict(
            safety_score=[0, 0, 0],
            speed_score=[0, 0, 0],
            posture_score=[0, 0, 0]
        )
        rec = recommend.Recommendation(
            payload_dict=payload_dict1,
            rec_dic=recommend.default_rec_dic,
            threshold_dic=recommend.default_threshold_dic
        )
        lattice = rec.recommendation_lattice
        self.assertEqual({1: False, 2: False, 3: False,
                          4: False, 5: False, 6: False},
                         lattice)
    def test_recommendation_lattice2(self):
        payload_dict2 = dict(
            safety_score=[3.1, 4.1, 4.1],
            speed_score=[3.1, 3.1, 4.1],
            posture_score=[2.1, 2.1, 5.1]
        )
        rec2 = recommend.Recommendation(
            payload_dict=payload_dict2,
            rec_dic=recommend.default_rec_dic,
            threshold_dic=recommend.default_threshold_dic
        )
        lattice2 = rec2.recommendation_lattice
        self.assertEqual({1: True, 2: False, 3: False,
                          4: True, 5: True, 6: False},
                         lattice2)
    def test_rec_top_priority(self):
        payload_dict1 = dict(
            safety_score=[0, 0, 0],
            speed_score=[0, 0, 0],
            posture_score=[0, 0, 0]
        )
        rec = recommend.Recommendation(
            payload_dict=payload_dict1,
            rec_dic=recommend.default_rec_dic,
            threshold_dic=recommend.default_threshold_dic
        )
        rec_id = rec.rec_top_priority()
        self.assertEqual(None,
                         rec_id)
    def test_rec_top_priority2(self):
        payload_dict2 = dict(
            safety_score=[3.1, 3.1, 4.1],
            speed_score=[3.1, 3.1, 4.1],
            posture_score=[2.1, 2.1, 5.1]
        )
        rec = recommend.Recommendation(
            payload_dict=payload_dict2,
            rec_dic=recommend.default_rec_dic,
            threshold_dic=recommend.default_threshold_dic
        )
        rec_id = rec.rec_top_priority()
        self.assertEqual(4,
                         rec_id)
if __name__ == '__main__':
    unittest.main()