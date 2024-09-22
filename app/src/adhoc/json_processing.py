# Third-party packages
from loguru import logger
from sys import stderr

logger.remove()
logger.add(
    stderr,
    level="INFO",
    format="<cyan>[{file.name}:{line} - {function}()]</cyan> <green>{time:YYYY-MM-DD HH:mm:ss}</green> - {level} - <level>{message}</level>",
)

# Built-in packages
from typing import Dict, List, Set


def get_all_articles_from_journal(journal_dict: Dict) -> List:
    pubmed = journal_dict["referencedBy"]["pubmedArticles"]
    clinical_trials = journal_dict["referencedBy"]["clinicalTrials"]

    return [pubmed, clinical_trials]


def get_drugs_mentioned_by_journal(
    pubmed_of_journal: List,
    clinical_trials_of_journal: List,
    return_drug_names: bool = False,
) -> Set:
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
            non_clinical_trials_journals.add(
                journal["title"]
            )  # For logging purposes only
            output_drug_mentions = output_drug_mentions.union(
                set_drugs_mentioned_by_journal
            )

    non_clinical_trials_journals = list(non_clinical_trials_journals)

    logger.info(
        f"The drug {drug_name} was mentioned alongside the following drug names `{', '.join(list(output_drug_mentions))}` by these non-clinical trials referenced journals : `{', '.join(non_clinical_trials_journals)}`"
    )
    return output_drug_mentions
