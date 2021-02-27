"""Tests the active scores implementation.

@ author Jessie Zhang
Copyright Iterate Labs, Inc. 2018-
"""
import unittest
from productivity import active_score
import pandas as pd

from productivity.active_score import ActiveScore


class TestActiveScore(unittest.TestCase):
    def test_to_ranges(self):
        list_of_points_1 = []
        list_of_points_2 = [1]
        list_of_points_3 = [1, 5]
        list_of_points_4 = [1, 4, 5, 6, 7, 9]
        list_of_points_5 = [4, 5, 6, 7, 8, 9]

        self.assertEqual(active_score.to_ranges(list_of_points_1), [])
        self.assertEqual(active_score.to_ranges(list_of_points_2), [[1, 1]])
        self.assertEqual(active_score.to_ranges(list_of_points_3), [[1, 1], [5, 5]])
        self.assertEqual(
            active_score.to_ranges(list_of_points_4), [[1, 1], [4, 7], [9, 9]]
        )
        self.assertEqual(active_score.to_ranges(list_of_points_5), [[4, 9]])

    def test_slide_window_get_chunk_diff(self):
        list_of_points_0 = []
        list_of_points_1 = [1]
        list_of_points_2 = [1, 7, 4]
        list_of_points_3 = [14, 2, 34, 17, 49, 3, 26, 43, 26, 18, 50, 52, -5]

        self.assertEqual(active_score.slide_window_get_chunk_diff(list_of_points_0), [])
        self.assertEqual(
            active_score.slide_window_get_chunk_diff(list_of_points_1), [0]
        )
        self.assertEqual(
            active_score.slide_window_get_chunk_diff(list_of_points_2), [6]
        )
        self.assertEqual(
            active_score.slide_window_get_chunk_diff(list_of_points_3), [47, 48, 49]
        )
        self.assertEqual(
            active_score.slide_window_get_chunk_diff(
                list_of_points_3, time_chunk_len=3
            ),
            [32, 32, 32, 46, 46, 40, 17, 25, 32, 34],
        )

    def test_remove_short_regions(self):
        list_of_ranges_0 = []
        list_of_ranges_1 = [[1, 1]]
        list_of_ranges_2 = [[6, 20], [34, 50]]
        list_of_ranges_3 = [[1, 20], [34, 50], [80, 85], [90, 110]]

        self.assertEqual(active_score.remove_short_regions(list_of_ranges_0), [])
        self.assertEqual(active_score.remove_short_regions(list_of_ranges_1), [])
        self.assertEqual(
            active_score.remove_short_regions(list_of_ranges_2), [[34, 50]]
        )
        self.assertEqual(
            active_score.remove_short_regions(list_of_ranges_3),
            [[1, 20], [34, 50], [90, 110]],
        )

    def test_merge_close_regions(self):
        list_of_ranges_0 = []
        list_of_ranges_1 = [[1, 1]]
        list_of_ranges_2 = [[6, 20], [34, 50]]
        list_of_ranges_3 = [[1, 20], [34, 76], [80, 85], [90, 110]]

        self.assertEqual(active_score.merge_close_regions(list_of_ranges_0), [])
        self.assertEqual(active_score.merge_close_regions(list_of_ranges_1), [[1, 1]])
        self.assertEqual(active_score.merge_close_regions(list_of_ranges_2), [[6, 50]])
        self.assertEqual(active_score.merge_close_regions(list_of_ranges_3), [[1, 110]])

    def test_compute_regions_percentage(self):
        start = 0
        end = 150

        list_of_ranges_0 = []
        list_of_ranges_1 = [[1, 1]]
        list_of_ranges_2 = [[6, 20], [34, 50]]
        list_of_ranges_3 = [[1, 76], [80, 85], [90, 110]]

        percentage_0 = active_score.compute_regions_percentage(
            list_of_ranges_0, start, end
        )
        percentage_1 = active_score.compute_regions_percentage(
            list_of_ranges_1, start, end
        )
        percentage_2 = active_score.compute_regions_percentage(
            list_of_ranges_2, start, end
        )
        percentage_3 = active_score.compute_regions_percentage(
            list_of_ranges_3, start, end
        )

        self.assertTrue(abs(percentage_0 - 0.0) < 0.001)
        self.assertTrue(abs(percentage_1 - 0.0) < 0.001)
        self.assertTrue(abs(percentage_2 - 0.2) < 0.001)
        self.assertTrue(abs(percentage_3 - 0.6666) < 0.001)

    def test_compute_active_scores_on_small_data(self):
        file_path = "Demos/demo-data-with-delta/small_delta_data_sample_1.csv"
        data_to_compute = pd.read_csv(file_path)
        ac_test = ActiveScore(raw_delta_values=data_to_compute)
        active_report = ac_test.compute_active_scores()

        self.assertTrue(isinstance(active_report, dict))
        self.assertTrue("intense_active_score" in active_report.keys())
        self.assertTrue("mild_active_score" in active_report.keys())
        self.assertTrue(0 <= active_report["intense_active_score"] <= 1)
        self.assertTrue(0 <= active_report["mild_active_score"] <= 1)

    def test_compute_active_scores_on_none_data(self):
        data_to_compute = None
        ac_test = ActiveScore(raw_delta_values=data_to_compute)
        active_report = ac_test.compute_active_scores()

        self.assertTrue(isinstance(active_report, dict))
        self.assertTrue("intense_active_score" in active_report.keys())
        self.assertTrue("mild_active_score" in active_report.keys())
        self.assertTrue(active_report["intense_active_score"] is None)
        self.assertTrue(active_report["mild_active_score"] is None)

    def test_compute_active_scores_on_medium_data(self):
        file_path = "Demos/demo-data-with-delta/medium_delta_data_sample_1.csv"
        data_to_compute = pd.read_csv(file_path)
        ac_test = ActiveScore(raw_delta_values=data_to_compute)
        active_report = ac_test.compute_active_scores()

        self.assertTrue(isinstance(active_report, dict))
        self.assertTrue("intense_active_score" in active_report.keys())
        self.assertTrue("mild_active_score" in active_report.keys())
        self.assertTrue(0 <= active_report["intense_active_score"] <= 1)
        self.assertTrue(0 <= active_report["mild_active_score"] <= 1)

    # Large file exceeds size limit
    # def test_compute_active_scores_on_large_data(self):
    #     file_path = "Demos/demo-data-with-delta/large_delta_data_sample_1.csv"
    #     data_to_compute = pd.read_csv(file_path)
    #     ac_test = ActiveScore(raw_delta_values=data_to_compute)
    #     active_report = ac_test.compute_active_scores()
    #
    #     self.assertTrue(isinstance(active_report, dict))
    #     self.assertTrue("intense_active_score" in active_report.keys())
    #     self.assertTrue("mild_active_score" in active_report.keys())
    #     self.assertTrue(0 <= active_report["intense_active_score"] <= 1)
    #     self.assertTrue(0 <= active_report["mild_active_score"] <= 1)


# if __name__ == "__main__":
#     unittest.main()
