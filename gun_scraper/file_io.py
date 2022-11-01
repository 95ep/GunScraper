"""Module collecting functions for file I/O."""
import json
from pathlib import Path
import time
from typing import Dict, List

from loguru import logger

INDENT_LEVEL = 4


class GunScraperFileIOError(Exception):
    """Exception to raise if anything goes wrong in the file_io module."""

    def __init__(self, message: str) -> None:
        """Initialize an exception instance and log the message.

        Args:
            message (str): error message for the exception
        """
        super().__init__(message)
        logger.error(message)


def load_data_file(data_file: Path) -> Dict:
    """Load content of the data file.

    Args:
        data_file (Path): Path to data file

    Raises:
        GunScraperFileIOError: if the parent folder of the 'data_file' doesn't exist

    Returns:
        Dict: Content of the data file, or empty dict if it doesn't exist
    """
    if data_file.exists():
        logger.debug(f"Data file {data_file} exists")
        with open(data_file) as fp:
            data_content = json.load(fp)
        logger.debug(f"The following content loaded from file: {data_content}")
        return data_content
    else:
        logger.warning(f"Data file {data_file} doesn't exist.")
        if not data_file.parent.is_dir():
            raise GunScraperFileIOError(
                f"data_folder from config doesn't exist: {data_file.parent}"
            )
        return {}


def read_guns_from_file(data_file: Path) -> List[Dict]:
    """Read the guns stored in the data file.

    Args:
        data_file (Path): Path to file holding previously scraped guns

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
    """Write the list of guns to file.

    Args:
        guns_list (List[Dict]): List of guns found during scraping
        data_file (Path): path to file holding scraped guns
    """
    data_content = load_data_file(data_file)

    logger.debug(f"Writing the following list of found guns to file: {guns_list}")
    data_content["found_guns"] = guns_list

    with open(data_file, "w") as fp:
        logger.debug(f"New data file content: {data_content}")
        json.dump(data_content, fp, indent=INDENT_LEVEL)


def read_notification_timestamp_from_file(data_file: Path) -> float:
    """Read timestamp (relative epoch) of latest notification from file.

    Args:
        data_file (Path): path to file holding scraped guns

    Returns:
        float: Timestamp of latest notification, 0 if file doesn't exist
    """
    data_content = load_data_file(data_file)
    if data_content:
        timestamp = data_content["latest_notification_timestamp"]
    else:
        timestamp = 0.0
    logger.debug(f"The following timestamp loaded from file: {timestamp}")

    return timestamp


def write_notification_timestamp_to_file(data_file: Path) -> None:
    """Write timestamp of latest notification to file.

    Args:
        data_file (Path): path to file holding scraped guns
    """
    data_content = load_data_file(data_file)

    timestamp = time.time()
    logger.debug(f"Writing the following timestamp to file: {timestamp}")
    data_content["latest_notification_timestamp"] = timestamp

    with open(data_file, "w") as fp:
        logger.debug(f"New data file content: {data_content}")
        json.dump(data_content, fp, indent=INDENT_LEVEL)
