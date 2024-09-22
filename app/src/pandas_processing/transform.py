# Third-party packages
import pandas as pd
from pandera.typing import DataFrame
from loguru import logger
from sys import stderr

logger.remove()
logger.add(
    stderr,
    level="INFO",
    format="<cyan>[{file.name}:{line} - {function}()]</cyan> <green>{time:YYYY-MM-DD HH:mm:ss}</green> - {level} - <level>{message}</level>",
)

# Built-in packages
from typing import Dict, List

# My Custom packages
from app.src.graph_linkage.journal_mentions import JournalMentions


def merge_dataframes(list_dataframes: List) -> DataFrame:
    return pd.concat(list_dataframes)


def merge_rows(group):
    """
    This function fills all missing data by using values from other instances of the same row (duplicates).
    Once the rows are merged, it then removes duplicates, returning only a single row per unique entry (ID).

    Parameters:
        - group (DataFrame): A pandas DataFrame Group (grouped on title and mentiond ate).

    Returns:
        - DataFrame: A single row with missing values filled and duplicates dropped.
    """

    """"""
    return group.ffill().bfill().iloc[0]


def build_link_graph_from_df(
    df_articles_cleaned: DataFrame, df_drugs_cleaned: DataFrame
) -> Dict:
    """
    Builds a link graph from cleaned article and drug DataFrames. Check the class functions' docstring for more details.

    Args:
        - df_articles_cleaned (DataFrame): DataFrame containing cleaned article data.
        - df_drugs_cleaned (DataFrame): DataFrame containing cleaned drug data.

    Returns:
        - Dict: A dictionary representing the link graph with journals and their related articles and drug mentions.
    """
    # Get the list of all journals
    list_distinct_journals = df_articles_cleaned["journal"].unique()

    output_dict = {"journals": []}

    for journal in list_distinct_journals:
        logger.info(f"Currently generating graph for {journal}")
        articles_of_journal_condition = df_articles_cleaned["journal"] == journal

        df_articles_of_journal = df_articles_cleaned[articles_of_journal_condition]

        journal_instance = JournalMentions(
            title=journal,
            drugs_dataFrame=df_drugs_cleaned,
            journal_articles_dataFrame=df_articles_of_journal,
        )

        current_graph_dict = journal_instance.generate_article_link_graph_dict()
        output_dict["journals"].append(current_graph_dict)

    return output_dict
