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
    path_split = output_filepath.split("/")
    current_path = ""

    for folder in path_split:
        if "." not in folder and not os.path.exists(folder):
            current_path += folder + "/"
            os.makedirs(current_path)


def write_dict_to_file(output_filepath: str, dictionary: Dict) -> None:
    create_folders_if_not_exist(output_filepath)

    with open(output_filepath, "w", encoding="utf-8") as hd:
        json.dump(dictionary, hd, indent=4, ensure_ascii=False)


def fix_broken_json(filepath: str) -> Dict:
    """When the json file is broken (trailing commas), we will cleaned it and import it as dictionary then load the dataframe"""
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
    try:
        with open(filepath, "r", encoding="utf-8") as hd:
            return json.load(hd)

    except ValueError:
        logger.warning(
            f"Broken json detected in {filepath}. Attempting to clean it and re-load it."
        )
        return fix_broken_json(filepath)
