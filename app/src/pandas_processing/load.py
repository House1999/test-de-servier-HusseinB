# Third-party packages
import pandas as pd
from pandera.typing import DataFrame

# Built-in packages
from typing import Dict, List

# My custom packages
from app.utils.my_logger import logger
import app.utils.files_processing as P
import app.src.pandas_processing.transform as T


def load_df_from_csv(filepath: str, delimiter: str = ",", header: int = 0) -> DataFrame:
    return pd.read_csv(filepath, delimiter=delimiter, header=header)


def load_df_from_json(filepath: str) -> DataFrame:
    return pd.read_json(filepath)


def load_df_from_dict(dictionary: Dict) -> DataFrame:
    return pd.DataFrame.from_dict(dictionary)


def load_input_data(paths: List) -> DataFrame:
    """
    Loads the project's input data from a list of file paths (provided via arguments).
    When multiple input files are detected (example : 2 PubMed files), they are all merged into a single dataframes.

    Parameters:
        - paths (List): A list of file paths containing data in CSV or JSON format.

    Returns:
        - df: Dataframe containing data from one or multiple input files.
    """
    list_dfs = []

    for path in paths:
        if path.endswith(".csv"):
            df = load_df_from_csv(path)

        elif path.endswith(".json"):
            try:
                df = load_df_from_json(path)
            except ValueError:
                logger.warning(
                    f"Broken json detected in {path}. Attempting to clean it and re-load it."
                )
                fixed_json = P.fix_broken_json(path)
                df = load_df_from_dict(fixed_json)

        else:
            raise Exception(
                f"The provided path {path} has an incompatible file extension (not csv nor json)."
            )

        list_dfs.append(df)

    df = T.merge_dataframes(list_dfs)

    logger.info(f"[Loading] - Successfully loaded and merged dataframes from {paths}.")
    return df
