# Third-party packages
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

# Built-in packages
import unittest
from datetime import datetime

# My Custom packages
from app.src.pandas_processing.clean import (
    normalize_dates_format,
    clean_titles,
    fill_in_missing_ids_int,
    drop_empty_titles_and_journals,
)


class TestClean(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run once per class instance"""
        # Input Data
        cls.input_data = {
            "id": [1, 2, 3, np.nan, 4, np.nan, 5],
            "title": [
                "Article, Title, with, lots-of; punctuations!",
                r"Mon titre en français avec des accents é è à \x28\xc5",
                "Article title with lots-of punctuations",
                "      title   with lots    of whitespaces    ",
                "    ",
                np.nan,
                "My Article",
            ],
            "date": [
                "01/04/2020",
                "2020-05-12",
                "1 April 2020",
                "2 January 2021",
                "15-07-2021",
                "05/12/2022",
                "07/09/2024",
            ],
            "journal": [
                np.nan,
                "  Journal de \x23 Génève ",
                "Journal wIth MulTiple CaSeS",
                "  Journal   de (Génève)  ",
                "MY  JOURNAL   ",
                "Totally normal journal",
                "",
            ],
        }

        # Expected data
        cls.expected_output = {
            "id": [1, 2, 3, 6, 4, 7, 5],
            "title": [
                "Article Title With Lots-Of Punctuations",
                "Mon Titre En Français Avec Des Accents É È À",
                "Article Title With Lots-Of Punctuations",
                "Title With Lots Of Whitespaces",
                "",
                "",
                "My Article",
            ],
            "date": [
                "2020-04-01",
                "2020-05-12",
                "2020-04-01",
                "2021-01-02",
                "2021-07-15",
                "2022-12-05",
                "2024-09-07",
            ],
            "journal": [
                "",
                "Journal De Génève",
                "Journal With Multiple Cases",
                "Journal De Génève",
                "My Journal",
                "Totally Normal Journal",
                "",
            ],
        }

    def setUp(self):
        """Run before each test"""
        self.input_df = pd.DataFrame(self.input_data)
        self.expected_df = pd.DataFrame(self.expected_output)

    def tearDown(self):
        """Run after each test, resetting the dataframes"""
        self.input_df = pd.DataFrame(self.input_data)
        self.expected_df = pd.DataFrame(self.expected_output)

    def test_date_format_normalization(self):
        self.expected_df["date"] = self.expected_df["date"].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%d")
        )

        # Run the function
        result_df = normalize_dates_format(self.input_df, "date", "%Y-%m-%d")

        # Assertions
        assert_series_equal(result_df["date"], self.expected_df["date"])

    def test_cleaning_strings(self):
        # Run the function
        result_df = self.input_df.copy()
        result_df["title"] = result_df["title"].apply(clean_titles)
        result_df["journal"] = result_df["journal"].apply(clean_titles)

        # Assertions
        assert_series_equal(result_df["title"], self.expected_df["title"])
        assert_series_equal(result_df["journal"], self.expected_df["journal"])

    def test_filling_missing_ids_no_overrides(self):
        """Check that the original IDs are not overwritten."""
        # Run the function
        result_df = fill_in_missing_ids_int(self.input_df, "id")

        # Assertions
        assert_series_equal(result_df["id"], self.expected_df["id"])

    def test_dropping_empty_titles_journals_only(self):
        # Expected output
        expected_data = {
            "id": [2, 3, np.nan, 4],
            "title": [
                r"Mon titre en français avec des accents é è à \x28\xc5",
                "Article title with lots-of punctuations",
                "      title   with lots    of whitespaces    ",
                "    ",
            ],
            "date": [
                "2020-05-12",
                "1 April 2020",
                "2 January 2021",
                "15-07-2021",
            ],
            "journal": [
                "  Journal de \x23 Génève ",
                "Journal wIth MulTiple CaSeS",
                "  Journal   de (Génève)  ",
                "MY  JOURNAL   ",
            ],
        }
        expected_df = pd.DataFrame(expected_data, index=[1, 2, 3, 4])

        # Run the function
        result_df = drop_empty_titles_and_journals(self.input_df)

        # Assertions
        assert_frame_equal(result_df, expected_df)


if __name__ == "__main__":
    unittest.main()
