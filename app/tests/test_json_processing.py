# Built-in packages
import unittest

# My Custom packages
from app.src.adhoc.json_processing import (
    get_drugs_mentioned_by_journal,
    get_all_articles_from_journal,
)


class TestJsonProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pubmed_of_journal = [
            {
                "articleId": "1",
                "articleTitle": "Aricle 1",
                "mentionDate": "2019-01-01",
                "mentionedDrugID": "D001",
                "mentionedDrugName": "DrugB",
            },
            {"mentionedDrugID": "D002", "mentionedDrugName": "DrugC"},
        ]

        cls.clinical_trials_of_journal = [
            {
                "articleTitle": "Aricle 3",
                "mentionedDrugID": "D001",
                "mentionedDrugName": "DrugB",
            },
            {
                "articleId": "4",
                "articleTitle": "Aricle 4",
                "mentionDate": "2020-05-01",
                "mentionedDrugID": "D005",
                "mentionedDrugName": "DrugD",
            },
            {
                "articleId": "5",
                "articleTitle": "Aricle 5",
                "mentionDate": "2020-06-01",
                "mentionedDrugID": "D007",
                "mentionedDrugName": "DrugF",
            },
        ]

        # 4 different types of journals
        cls.journal_dict_complete = {
            "title": "Test Journal Title",
            "referencedBy": {
                "pubmedArticles": cls.pubmed_of_journal,
                "clinicalTrials": cls.clinical_trials_of_journal,
            },
        }

        cls.journal_dict_pubmed_only = {
            "title": "Test Journal Title",
            "referencedBy": {
                "pubmedArticles": cls.pubmed_of_journal,
                "clinicalTrials": [],
            },
        }

        cls.journal_dict_clinical_only = {
            "title": "Test Journal Title",
            "referencedBy": {
                "pubmedArticles": [],
                "clinicalTrials": cls.clinical_trials_of_journal,
            },
        }

        cls.journal_dict_empty = {
            "title": "Test Journal Title",
            "referencedBy": {
                "pubmedArticles": [],
                "clinicalTrials": [],
            },
        }

    def test_handles_missing_keys_in_articles(self):
        """Handles cases where the article object has missing keys (other than the drug-relted keys)."""
        result = get_drugs_mentioned_by_journal(
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
            return_drug_names=False,
        )
        expected_result = {"D001", "D002", "D005", "D007"}
        self.assertEqual(result, expected_result)

    def test_returns_drug_ids_when_return_drug_names_is_false(self):
        result = get_drugs_mentioned_by_journal(
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
            return_drug_names=False,
        )
        expected_result = {"D001", "D002", "D005", "D007"}
        self.assertEqual(result, expected_result)

    def test_returns_drug_names_when_return_drug_names_is_true(self):
        result = get_drugs_mentioned_by_journal(
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
            return_drug_names=True,
        )
        expected_result = {"DrugB", "DrugC", "DrugD", "DrugF"}
        self.assertEqual(result, expected_result)

    def test_extract_articles_from_journal_dict(self):
        # Expectations
        expected_result_complete = [
            self.pubmed_of_journal,
            self.clinical_trials_of_journal,
        ]
        expected_result_pubmed_only = [self.pubmed_of_journal, []]
        expected_result_clinical_only = [[], self.clinical_trials_of_journal]
        expected_result_empty = [[], []]

        # Run function
        result_complete = get_all_articles_from_journal(self.journal_dict_complete)
        result_pubmed_only = get_all_articles_from_journal(
            self.journal_dict_pubmed_only
        )
        result_clinical_only = get_all_articles_from_journal(
            self.journal_dict_clinical_only
        )
        result_empty = get_all_articles_from_journal(self.journal_dict_empty)

        # Assertions
        self.assertEqual(result_complete, expected_result_complete)
        self.assertEqual(result_pubmed_only, expected_result_pubmed_only)
        self.assertEqual(result_clinical_only, expected_result_clinical_only)
        self.assertEqual(result_empty, expected_result_empty)

    def test_journal_dict_missing_keys(self):
        journal_dict_no_keys = {}
        journal_dict_no_referenced_by = {"title": "myArticle"}
        journal_dict_no_clinical = {
            "title": "myArticle",
            "referencedBy": {"pubmedArticles": []},
        }
        journal_dict_no_pubmed = {
            "title": "myArticle",
            "referencedBy": {"clinicalTrials": []},
        }

        # Check that the dictionaries raises errors
        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_keys)

        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_referenced_by)

        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_clinical)

        with self.assertRaises(KeyError):
            get_all_articles_from_journal(journal_dict_no_pubmed)

        # Check that well formed dictionaries do NOT raise errors
        get_all_articles_from_journal(self.journal_dict_complete)
        get_all_articles_from_journal(self.journal_dict_pubmed_only)
        get_all_articles_from_journal(self.journal_dict_clinical_only)
        get_all_articles_from_journal(self.journal_dict_empty)


if __name__ == "__main__":
    unittest.main()
