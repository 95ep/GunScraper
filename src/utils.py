"""Module containing utilities functions for GunScraper."""
from bs4 import BeautifulSoup
from loguru import logger
import requests


def soup_from_url(url: str) -> BeautifulSoup:
    """Return BeautifulSoup object that parses html content on provided url.

    Args:
        url (str): url to the page to parse

    Returns:
        BeautifulSoup: BeautifulSoup object representing the html content
    """
    logger.debug(f"Requesting {url}")
    response = requests.get(url)
    logger.debug("Response retrieved")
    return BeautifulSoup(response.content, "html.parser")
