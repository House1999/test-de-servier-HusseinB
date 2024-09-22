# Built-in packages
from typing import Dict, List, Set

# My Custom packages
from app.utils.my_logger import logger


def get_all_articles_from_journal(journal_dict: Dict) -> List:
    """
    Extracts the list PubMed articles and clinical trials referencing a given journal.

    Parameters:
        - journal_dict (Dict): A dictionary containing information about the journal.

    Returns:
        - List: A list containing PubMed articles and clinical trials.
    """
    if (
        "referencedBy" not in journal_dict
        or "pubmedArticles" not in journal_dict["referencedBy"]
        or "clinicalTrials" not in journal_dict["referencedBy"]
    ):
        raise KeyError(
            f"The following journal is broken and missing important keys : {journal_dict} "
        )

    pubmed = journal_dict["referencedBy"]["pubmedArticles"]
    clinical_trials = journal_dict["referencedBy"]["clinicalTrials"]

    return [pubmed, clinical_trials]


def get_drugs_mentioned_by_journal(
    pubmed_of_journal: List,
    clinical_trials_of_journal: List,
    return_drug_names: bool = False,
) -> Set:
    """
    Return a set of drugs mentioned by all articles (PubMed and clinical trials) of a given journal.

    Parameters:
        - pubmed_of_journal (List): List of PubMed articles referencing the journal.
        - clinical_trials_of_journal (List): List of clinical trials referencing the journal.
        - return_drug_names (bool, optional): Flag to determine whether to return drug names or IDs. Defaults to False.

    Returns:
        - mentioned_drugs_no_duplicates: Set of mentioned drugs, without duplicates.
    """
    mentioned_drugs_no_duplicates = set()
    all_articles = pubmed_of_journal + clinical_trials_of_journal

    for article_object in all_articles:
        if return_drug_names:
            mentioned_drugs_no_duplicates.add(article_object["mentionedDrugName"])
        else:
            mentioned_drugs_no_duplicates.add(article_object["mentionedDrugID"])

    return mentioned_drugs_no_duplicates


def get_drugs_mentioned_by_similar_journals(
    list_journals: List, drug_name: str, skip_clinical_trials: bool
) -> Set:
    """
    Return a set of drugs mentioned alongside a specific drug, only mentioned by non-clinical trials referenced journals.

    Parameters:
        - list_journals (List): List of all journals.
        - drug_name (str): The specific drug name to search for.
        - skip_clinical_trials (bool): Flag to skip journals referenced by clinical trials.

    Returns:
        - output_drug_mentions: Set of drugs mentioned alongside the specific drug name.
    """
    output_drug_mentions = set()
    non_clinical_trials_journals = set()  # For logging purposes only

    for journal in list_journals:
        pubmed, clinical_trials = get_all_articles_from_journal(journal)

        if clinical_trials != [] and skip_clinical_trials:
            # Skip journals that are referenced by clinical trials
            continue

        set_drugs_mentioned_by_journal = get_drugs_mentioned_by_journal(
            pubmed_of_journal=pubmed,
            clinical_trials_of_journal=clinical_trials,
            return_drug_names=True,
        )

        if drug_name in set_drugs_mentioned_by_journal:
            output_drug_mentions = output_drug_mentions.union(
                set_drugs_mentioned_by_journal
            )
            # For logging purposes only
            non_clinical_trials_journals.add(journal["title"])

    non_clinical_trials_journals = list(non_clinical_trials_journals)

    logger.info(
        f"The drug {drug_name} was mentioned alongside the following drug names `{', '.join(list(output_drug_mentions))}` by these non-clinical trials referenced journals : `{', '.join(non_clinical_trials_journals)}`"
    )
    return output_drug_mentions
