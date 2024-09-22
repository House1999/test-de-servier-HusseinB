# Third-party packages
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

# Built-in packages
import unittest

# My custom packages
from app.src.pandas_processing.transform import merge_rows


class TestTransform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run once per class instance"""
        # Input Data
        cls.input_data = {
            "id": [1, 2, np.nan, np.nan, 4, 5],
            "title": [
                "A 44-year-old man with erythema of the face diphenhydramine, neck, and chest, weakness, and palpitation",
                "Tetracycline Resistance Patterns of Lactobacillus buchneri Group Strains",
                "A 44-year-old man with erythema of the face diphenhydramine, neck, and chest, weakness, and palpitation",
                "The High Cost of Epinephrine Autoinjectors and Possible Alternatives.",
                "Time to epinephrine treatment is associated with the risk of mortality in children who achieve sustained ROSC after traumatic out-of-hospital cardiac arrest.",
                "Tetracycline Resistance Patterns of Lactobacillus buchneri Group Strains",
            ],
            "date": [
                "2020-04-01",
                "2020-05-12",
                "2020-04-01",
                "2021-02-01",
                "2021-07-15",
                "2020-05-15",
            ],
            "journal": [
                np.nan,
                "Hôpitaux Universitaires de Genève",
                "Journal of emergency nursing",
                "Journal of emergency nursing",
                "Hôpitaux Universitaires de Genève",
                np.nan,
            ],
        }

        # Expected data
        cls.expected_output = {
            "id": [1, 2, np.nan, 4, 5],
            "title": [
                "A 44-year-old man with erythema of the face diphenhydramine, neck, and chest, weakness, and palpitation",
                "Tetracycline Resistance Patterns of Lactobacillus buchneri Group Strains",
                "The High Cost of Epinephrine Autoinjectors and Possible Alternatives.",
                "Time to epinephrine treatment is associated with the risk of mortality in children who achieve sustained ROSC after traumatic out-of-hospital cardiac arrest.",
                "Tetracycline Resistance Patterns of Lactobacillus buchneri Group Strains",
            ],
            "date": [
                "2020-04-01",
                "2020-05-12",
                "2021-02-01",
                "2021-07-15",
                "2020-05-15",
            ],
            "journal": [
                "Journal of emergency nursing",
                "Hôpitaux Universitaires de Genève",
                "Journal of emergency nursing",
                "Hôpitaux Universitaires de Genève",
                np.nan,
            ],
        }

    def setUp(self):
        """Run before each test"""
        self.input_df = pd.DataFrame(self.input_data)
        self.expected_df = pd.DataFrame(self.expected_output)

    def test_merge_rows(self):
        """
        This test will check that the rows are merged correctly. Three cases are studied :
            - Case 1 : When a row has the same title and mention date, they will be merged.
            - Case 2 : When a row has the same title but different mention date, they will NOT be merged.
            - Case 3 : We don't accidentally merge rows that are not similar
        """

        articles_group = self.input_df.groupby(["title", "date"], group_keys=False)[
            self.input_df.columns.tolist()
        ]
        result_df = articles_group.apply(merge_rows).reset_index(drop=True)

        # Sort so the IDs are in the correct order
        self.expected_df.sort_values("id", inplace=True, ignore_index=True)
        result_df.sort_values("id", inplace=True, ignore_index=True)

        # Assertions
        assert_frame_equal(result_df, self.expected_df)


if __name__ == "__main__":
    unittest.main()
