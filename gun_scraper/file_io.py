from loguru import logger
import json
from pathlib import Path
import time
from typing import Dict, List, Optional

from gun_scraper.main import GunScraperError

INDENT_LEVEL = 4


class GunScraperFileIOError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)
        logger.error(message)


def load_data_file(data_file: Path) -> Optional[Dict]:
    """Load content of the data file.

    Args:
        data_file (Path): Path to data file

    Raises:
        GunScraperFileIOError: if the parent folder of the 'data_file' doesn't exist

    Returns:
        Optional[Dict]: Content of the data file, or None if it doesn't exist
    """
    if data_file.exists():
        logger.debug(f"Data file {data_file} exists")
        with open(data_file) as fp:
            data_content = json.load(fp)
        logger.debug(f"The following content loaded from file: {data_content}")
    else:
        logger.warning(f"Data file {data_file} doesn't exist.")
        data_content = None
        if not data_file.parent.is_dir():
            raise GunScraperFileIOError(
                f"data_folder from config doesn't exist: {data_file.parent}"
            )

    return data_content


def read_guns_from_file(data_file: Path) -> List[Dict]:
    """Read the guns stored in the data file.

    Args:
        data_file (Path): Path to file holding previously scraped guns

    Raises:
        GunScraperError: if the parent folder of the 'data_file' doesn't exist

    Returns:
        List[Dict]: List of guns stored in the data file, empty if no such file exists
    """
    data_content = load_data_file(data_file)
    if data_content:
        guns_list = data_content["found_guns"]
    else:
        guns_list = []
    logger.debug(f"The following guns loaded from file: {guns_list}")

    return guns_list


def write_guns_to_file(guns_list: List[Dict], data_file: Path) -> None:
    """Write the found guns in list to file.

    Args:
        guns_list (List[Dict]): List of guns found during scraping
        data_file (Path): path to file holding scraped guns
    """
    data_content = load_data_file(data_file)
    if not data_content:
        # Create dict structure if file did not exist before
        data_content = {"timestamp": None, "found_guns": None}

    data_content["found_guns"] = guns_list

    with open(data_file, "w") as fp:
        logger.debug(f"New data file content: {data_content}")
        json.dump(data_content, fp, indent=INDENT_LEVEL)


def write_notification_timestamp_to_file(data_file: Path) -> None:
    data_content = load_data_file(data_file)
    timestamp = time.time()
    data_content["timestamp"] = timestamp
    logger.debug(f"Writing the following timestamp to file: {timestamp}")

    with open(data_file, "w") as fp:
        logger.debug(f"New data file content: {data_content}")
        json.dump(data_content, fp, indent=INDENT_LEVEL)
