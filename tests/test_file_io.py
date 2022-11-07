"""Unit tests for the file_io.py module."""
from json import dump, load
from pathlib import Path
from time import time
from typing import Callable, Dict

import pytest

from gun_scraper.file_io import (
    GunScraperFileIOError,
    load_data_file,
    read_guns_from_file,
    read_notification_timestamp_from_file,
    write_guns_to_file,
    write_notification_timestamp_to_file,
)


@pytest.fixture()
def data_folder(tmp_path: Path) -> Path:
    """Define a data folder for tests.

    Args:
        tmp_path (Path): temporary path fixture

    Returns:
        Path: path to temporary data folder
    """
    data_folder = tmp_path.joinpath("data")
    data_folder.mkdir()
    return data_folder


@pytest.fixture()
def create_data_file(data_folder: Path) -> Callable[[Dict], Path]:
    """Define function for creating data file for tests.

    Args:
        data_folder (Path): temporary data folder for tests

    Returns:
        Callable[[Dict], Path]: function to create the data file.
    """

    def _create_data_file(content: Dict):
        data_file = data_folder.joinpath("data.json")
        with open(data_file, "w") as fp:
            dump(content, fp)

        return data_file

    return _create_data_file


def test_load_data_file__data_file_missing(tmp_path: Path):
    """Test to load data file when data folder exists, but file is missing.

    Args:
        tmp_path (Path): temporary path fixture
    """
    data_folder = tmp_path.joinpath("data")
    data_folder.mkdir()
    data_file = data_folder.joinpath("data.json")

    assert load_data_file(data_file) == {}


def test_load_data_file__data_folder_missing(tmp_path: Path):
    """Test that exception is raised when the data folder is missing.

    Args:
        tmp_path (Path): temporary path fixture
    """
    data_folder = tmp_path.joinpath("data")
    data_file = data_folder.joinpath("data.json")

    with pytest.raises(
        GunScraperFileIOError,
        match=f"data_folder from config doesn't exist: {data_folder}",
    ):
        load_data_file(data_file)


def test_read_guns_from_file__gun_list_loaded(create_data_file: Callable[[Dict], Path]):
    """Test to load previously found guns from data file.

    Args:
        create_data_file (Callable[[Dict], Path]): fixture to define temporary data file
    """
    data_content = {"found_guns": [{"name": "gun_1"}, {"name": "gun_2"}]}
    data_file = create_data_file(data_content)

    assert read_guns_from_file(data_file) == data_content["found_guns"]


def test_read_guns_from_file__no_data_file_exists(data_folder: Path):
    """Test to load previously found guns when no data file exists.

    Args:
        data_folder (Path): temporary data folder for tests
    """
    data_file = data_folder.joinpath("data.json")

    assert read_guns_from_file(data_file) == []


def test_write_guns_to_file__gun_list_written(create_data_file: Callable[[Dict], Path]):
    """Test to write list of found guns to the data file.

    Args:
        create_data_file (Callable[[Dict], Path]): fixture to define temporary data file
    """
    original_content = {
        "found_guns": [{"name": "gun_1"}, {"name": "gun_2"}],
        "foo": "bar",
    }
    data_file = create_data_file(original_content)

    new_guns = [{"name": "gun_2"}, {"name": "gun_3"}]

    write_guns_to_file(new_guns, data_file)

    with open(data_file, "r") as fp:
        new_data_content = load(fp)

    assert new_data_content["found_guns"] == new_guns
    assert new_data_content["foo"] == "bar"


def test_read_notification_timestamp_from_file__timestamp_loaded(
    create_data_file: Callable[[Dict], Path]
):
    """Test to load notification timestamp from data file.

    Args:
        create_data_file (Callable[[Dict], Path]): fixture to define temporary data file
    """
    timestamp = time()
    data_content = {"latest_notification_timestamp": timestamp}
    data_file = create_data_file(data_content)

    assert read_notification_timestamp_from_file(data_file) == timestamp


def test_read_notification_timestamp_from_file__no_data_file_exists(data_folder: Path):
    """Test to load notification timestamp when no data file exists.

    Args:
        data_folder (Path): temporary data folder for tests
    """
    data_file = data_folder.joinpath("data.json")

    assert read_notification_timestamp_from_file(data_file) == 0.0


def test_write_notification_timestamp_to_file__timestamp_written(
    create_data_file: Callable[[Dict], Path], mocker
):
    """Test to write notification timestamp to the data file.

    Args:
        create_data_file (Callable[[Dict], Path]): fixture to define temporary data file
        mocker: Pytest mock object
    """
    original_content = {
        "found_guns": [{"name": "gun_1"}, {"name": "gun_2"}],
        "latest_notification_timestamp": "1667747404.528576",
    }
    data_file = create_data_file(original_content)

    # Patch time() with fixed timestamp
    new_timestamp = 1667747461.199405
    mocker.patch("gun_scraper.file_io.time", return_value=new_timestamp)

    write_notification_timestamp_to_file(data_file)

    with open(data_file, "r") as fp:
        new_data_content = load(fp)

    assert new_data_content["latest_notification_timestamp"] == new_timestamp
    assert new_data_content["found_guns"] == original_content["found_guns"]
