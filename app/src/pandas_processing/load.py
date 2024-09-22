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

# My custom packages
from app.utils.files_processing import fix_broken_json
from app.src.pandas_processing.transform import merge_dataframes


def load_df_from_csv(filepath: str, delimiter: str = ",", header: int = 0) -> DataFrame:
    return pd.read_csv(filepath, delimiter=delimiter, header=header)


def load_df_from_json(filepath: str) -> DataFrame:
    return pd.read_json(filepath)


def load_df_from_dict(dictionary: Dict) -> DataFrame:
    return pd.DataFrame.from_dict(dictionary)


def load_input_data(paths: List) -> DataFrame:
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
                fixed_json = fix_broken_json(path)
                df = load_df_from_dict(fixed_json)

        else:
            raise Exception(
                f"The provided path {path} has an incompatible file extension (not csv nor json)."
            )

        list_dfs.append(df)

    df = merge_dataframes(list_dfs)

    logger.info(f"[Loading] - Successfully loaded and merged dataframes from {paths}.")
    return df
