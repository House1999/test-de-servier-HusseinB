# Third-party packages
import pandas as pd
from pandera.typing import DataFrame

# Built-in packages
import re
from typing import Dict, List
from datetime import datetime


def normalize_dates_format(
    df: DataFrame, date_column_name: str, output_date_format: str = "%Y-%m-%d"
) -> DataFrame:
    """
    The input files have multiple date formats (%d %B %Y, %d/%m/%Y and %Y-%m-%d).
    We want to standardize all of them to the %Y-%m-%d format.
    We could have done this inside the `pd.read_csv()` function but here we use `pd.to_datetime()` instead to detect all possible date formats.
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
    df[id_column_name] = df[id_column_name].astype(str)
    return df


def rename_column(df: DataFrame, column_naming_mapping: Dict) -> DataFrame:
    return df.rename(columns=column_naming_mapping)


def fill_in_missing_ids_int(df: DataFrame, id_column_name: str) -> DataFrame:
    # This only works if id is integer
    df[id_column_name] = pd.to_numeric(df[id_column_name], errors="coerce")

    max_id = int(df[id_column_name].max())
    number_missing_rows = df[id_column_name].isna().sum()

    id_range = range(int(max_id) + 1, int(max_id) + 1 + number_missing_rows)

    df.loc[df[id_column_name].isna(), id_column_name] = id_range
    df[id_column_name] = df[id_column_name].astype(int)
    return df


def clean_titles(articleTitle: str) -> str:
    # Remove encoding issues like \xc3\x28, we are focusing solely on \x followed by 2 characters or digits
    articleTitle = re.sub(r"\\x[0-9a-fA-F]{2}", "", articleTitle)

    # Remove punctuations except hyphens "-"
    articleTitle = re.sub(r"[^\w\s&À-ÿ-]", "", articleTitle)

    # Title Case
    articleTitle = articleTitle.title()

    # Normalize number of spaces (remove extra spaces)
    articleTitle = re.sub(r"\s+", " ", articleTitle)

    # Remove trailing spaces
    articleTitle = articleTitle.strip()

    return articleTitle


def drop_empty_titles_and_journals(df: DataFrame) -> DataFrame:
    drop_condition = (df["title"] == "") | (df["journal"] == "")
    filtered_df = df[~drop_condition]
    return filtered_df


def drop_duplicate_ids_then_index(
    drugs_df: DataFrame, all_articles_df: DataFrame
) -> List:
    drugs_df.drop_duplicates(subset=["atccode"], keep="first", inplace=True)
    all_articles_df.drop_duplicates(subset=["id"], keep="first", inplace=True)

    # Index the dataframes using IDs
    drugs_df.set_index("atccode", inplace=True)
    all_articles_df.set_index("id", inplace=True)

    return drugs_df, all_articles_df
