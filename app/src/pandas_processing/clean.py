# Third-party packages
import pandas as pd
from pandera.typing import DataFrame
import numpy as np

# Built-in packages
import re
from typing import Dict, List
from datetime import datetime


def normalize_dates_format(
    df: DataFrame, date_column_name: str, output_date_format: str = "%Y-%m-%d"
) -> DataFrame:
    """
    Standardizes the date format in the specified DataFrame column to the given output date format. The input files have multiple date formats (%d %B %Y, %d/%m/%Y and %Y-%m-%d).
    We could have done this inside the `pd.read_csv()` function but here we use `pd.to_datetime()` instead to detect all possible date formats.

    Parameters:
        - df (DataFrame): DataFrame containing the date column to be normalized.
        - date_column_name (str): Name of the column containing dates to be standardized.
        - output_date_format (str): Desired output date format (default is "%Y-%m-%d").

    Returns:
        - df: DataFrame with the date column standardized to the output date format.
    """
    df[date_column_name] = pd.to_datetime(
        df[date_column_name], dayfirst=True, format="mixed"
    )
    df[date_column_name] = df[date_column_name].dt.strftime(output_date_format)
    df[date_column_name] = df[date_column_name].apply(
        lambda x: datetime.strptime(x, output_date_format)
    )
    return df


def cast_id_as_string(df: DataFrame, id_column_name: str) -> DataFrame:
    """
    Cast the specified column in the DataFrame as a string type.

    Parameters:
        - df (DataFrame): The input pandas DataFrame.
        - id_column_name (str): The name of the column to be cast as string.

    Returns:
        df: The DataFrame with the specified column cast as string.
    """
    df[id_column_name] = df[id_column_name].astype(str)
    return df


def rename_column(df: DataFrame, column_naming_mapping: Dict) -> DataFrame:
    """
    Rename one or multiple columns in a DataFrame.

    Parameters:
        - df (DataFrame): The input pandas DataFrame.
        - column_naming_mapping (Dict): The renaming mapping where the key is the old name and the value is the new name.

    Returns:
        df: The DatFrame with the new names.
    """
    return df.rename(columns=column_naming_mapping)


def fill_in_missing_ids_int(df: DataFrame, id_column_name: str) -> DataFrame:
    """
    Fill in missing integer IDs in the specified DataFrame column. This only works if the ID is an integer.

    Parameters:
        - df (DataFrame): DataFrame to process
        - id_column_name (str): Name of the column containing IDs. Should be numeric

    Returns:
        - df: DataFrame with missing IDs filled in
    """
    df[id_column_name] = pd.to_numeric(df[id_column_name], errors="coerce")

    max_id = int(df[id_column_name].max())
    number_missing_rows = df[id_column_name].isna().sum()

    id_range = range(int(max_id) + 1, int(max_id) + 1 + number_missing_rows)

    df.loc[df[id_column_name].isna(), id_column_name] = id_range
    df[id_column_name] = df[id_column_name].astype(int)
    return df


def clean_titles(current_title: str) -> str:
    """
    Clean a given article or journal title in order to be able to detect recurrences of each even with typos. Check the code below to see the list of actions.

    Args:
        - current_title (str): The title of the article or journalto be cleaned.

    Returns:
        current_title: The cleaned title.
    """
    if not pd.isna(current_title):
        # Remove encoding issues like \xc3\x28, we are focusing solely on \x followed by 2 characters or digits
        current_title = re.sub(r"\\x[0-9a-fA-F]{2}", "", current_title)

        # Remove punctuations except hyphens "-"
        current_title = re.sub(r"[^\w\s&ÀàÀ-ÿ-]", "", current_title)

        # Convert to title case
        current_title = current_title.title()

        # Normalize number of spaces (remove extra spaces)
        current_title = re.sub(r"\s+", " ", current_title)

        # Remove trailing spaces
        current_title = current_title.strip()

        return current_title

    return ""  # Will be cleaned in the next steps


def drop_empty_titles_and_journals(df: DataFrame) -> DataFrame:
    """
    Drops rows from the input DataFrame where either the 'title' or 'journal' column is empty.

    Parameters:
        - df (DataFrame): Input DataFrame of articles (PubMed and clinical trials)

    Returns:
        - filtered_df: The dataFrame without rows containing empty 'title' or 'journal' values.
    """
    filter_condition = (
        (df["title"] != "")
        & (pd.notna(df["title"]))
        & (df["journal"] != "")
        & (pd.notna(df["journal"]))
    )

    filtered_df = df[filter_condition]
    return filtered_df


def drop_duplicate_ids_then_index(
    drugs_df: DataFrame, all_articles_df: DataFrame
) -> List:
    """
    Drop duplicate IDs from the projects' DataFrames, then index them using the ID column.

    Parameters:
        - drugs_df: DataFrame containing drug data.
        - all_articles_df: DataFrame containing all articles data.

    Returns:
        - A tuple containing the modified drugs DataFrame and articles DataFrame.
    """
    drugs_df = drugs_df.drop_duplicates(
        subset=["atccode"], keep="first", ignore_index=True
    )
    all_articles_df = all_articles_df.drop_duplicates(
        subset=["id"], keep="first", ignore_index=True
    )

    # Index the dataframes using IDs
    drugs_df.set_index("atccode", inplace=True)
    all_articles_df.set_index("id", inplace=True)

    return drugs_df, all_articles_df
