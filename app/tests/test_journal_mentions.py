# Third-party packages
import pandas as pd

# Built-in packages
import unittest

# My Custom packages
from app.src.constants import DRUGS_PATHS
from app.src.graph_linkage.journal_mentions import JournalMentions
import app.src.pandas_processing.load as L


class TestJournalMentions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.drugs_df = L.load_df_from_csv(DRUGS_PATHS)
        cls.drugs_df.rename(columns={"drug": "name"}, inplace=True)
        cls.drugs_df["name"] = cls.drugs_df["name"].apply(lambda x: x.title())
        cls.drugs_df.set_index("atccode", inplace=True)

    def setUp(self):
        self.jm = JournalMentions(
            title="Test Journal",
            drugs_dataFrame=self.drugs_df,
            journal_articles_dataFrame=pd.DataFrame(),  # Not needed for the test
        )

        self.article_mentions_counter = {
            "Comparison Of Pressure Release Phonophoresis And Dry Needling In Treatment Of Latent Myofascial Trigger Point Of Upper Trapezius Muscle": [],
            "A 44-year-old man with erythema of the face Diphenhydramine , neck, and chest, weakness, and palpitations": [
                ["A04AD", "Diphenhydramine"]
            ],
            "Tetracycline and Ethanol helps symptoms of ciguatera fish poisoning": [
                ["S03AA", "Tetracycline"],
                ["V03AB", "Ethanol"],
            ],
            "Appositional Tetracycline bone formation rates in the Beagle. In other news, Isoprenaline and Atropine ...": [
                ["S03AA", "Tetracycline"],
                ["6302001", "Isoprenaline"],
                ["A03BA", "Atropine"],
            ],
        }

    def test_drug_mentions_in_title(self):
        """
        This function will test if we can correctly detect drug names.
        Since we are only testing the mentions (not the cleaning), the drug names are uppercase and not titlecase.
        """
        for article_title, mentioned_drugs in self.article_mentions_counter.items():
            current_article_mentions = self.jm.extract_drug_from_publication_title(
                article_title
            )

            current_article_mentions = sorted(
                current_article_mentions, key=lambda x: x[0]
            )
            expected_article_mentions = sorted(mentioned_drugs, key=lambda x: x[0])

            self.assertEqual(current_article_mentions, expected_article_mentions)


if __name__ == "__main__":
    unittest.main()
