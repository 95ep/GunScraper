"""Tests for __main__.py module."""
import pytest

from gun_scraper.__main__ import parse_args


@pytest.mark.parametrize(
    ("config_file_args"), [("-c", "foo"), ("--config-file", "bar")]
)
def test_parse_args__config_file_successfully_parsed(mocker, config_file_args):
    """Test that config file command line argument gets parsed correctly.

    Args:
        mocker: fixture for mocking
        config_file_args (str): passed config file argument
    """
    mocker.patch("sys.argv", ["gun_scraper", *config_file_args])

    assert parse_args().config_file == config_file_args[1]
