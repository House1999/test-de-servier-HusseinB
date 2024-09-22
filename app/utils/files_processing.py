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
import os
import json
from typing import Dict


def create_folders_if_not_exist(output_filepath: str) -> None:
    """
    Create folders if they do not exist based on the provided output file path.

    Parameters:
        - output_filepath (str): The path to the output file.
    """
    path_split = output_filepath.split("/")
    current_path = ""

    for folder in path_split:
        if "." not in folder and not os.path.exists(folder):
            current_path += folder + "/"
            os.makedirs(current_path)


def write_dict_to_file(output_filepath: str, dictionary: Dict) -> None:
    """
    Write a dictionary to a file.

    Parameters:
        - output_filepath (str): The path to the output file.
        - dictionary (Dict): The dictionary to be written to the file.
    """
    create_folders_if_not_exist(output_filepath)

    with open(output_filepath, "w", encoding="utf-8") as hd:
        json.dump(dictionary, hd, indent=4, ensure_ascii=False)


def fix_broken_json(filepath: str) -> Dict:
    """
    Fixes a broken JSON file (trailing commas) by cleaning it and importing it as a dictionary, then loads the dataframe.

    Parameters:
        - filepath (str): The path to the JSON file.

    Returns:
        - cleaned_json: The cleaned JSON data as a dictionary.
    """
    with open(filepath, "r", encoding="utf-8") as hd:
        json_str = hd.read()

    json_str = (
        json_str.replace("null", "None")
        .replace("true", "True")
        .replace("false", "False")
    )
    cleaned_json = eval(json_str)

    logger.info(f"Successfully fixed and loaded the broken Json file.")
    return cleaned_json


def import_json_file_as_dict(filepath: str) -> Dict:
    """
    Imports a JSON file as a dictionary.

    Parameters:
        - filepath (str): The path to the JSON file.

    Returns:
        - Dict: The JSON data loaded as a dictionary.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as hd:
            return json.load(hd)

    except ValueError:
        logger.warning(
            f"Broken json detected in {filepath}. Attempting to clean it and re-load it."
        )
        return fix_broken_json(filepath)
