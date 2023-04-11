"""Abstract base class all site scraper should inherit."""
from abc import ABC, abstractmethod
from typing import Dict, List, Union

from loguru import logger


class ScraperError(Exception):
    """Exception to raise when something goes wrong in the scraper base class."""

    def __init__(self, message) -> None:
        """Create the error instance and log the error message.

        Args:
            message (str): the error message to log
        """
        super().__init__(message)
        logger.error(message)


# TODO: Check which of these methods maybe should be concrete instead


class GunScraperABC(ABC):
    """Abstract class for all site scrapers."""

    @abstractmethod
    def __init__(self, filter_input: Dict[str, str]):
        """Create the scraper object.

        Args:
            filter_input (Dict[str, str]): filter settings from config
        """

    def _parse_filters(self, filter_input: Dict[str, str]):
        """Parse the filter input.

        Args:
            filter_input (Dict[str, str]): filter settings from config

        Raises:
            JGScraperError: if an unsupported filter key is included
                in the input
        """
        logger.debug(f"Parsing filters: {filter_input}")
        for filter_key, filter_value in filter_input.items():
            if filter_value:  # Get rid of None
                if filter_key == "handedness":
                    self._set_handedness_filter(filter_value)
                elif filter_key == "caliber":
                    self._set_caliber_filter(filter_value)
                else:
                    raise ScraperError(f"Filter type '{filter_key}' not supported!")
        logger.debug("Filters parsed")

    def _set_caliber_filter(self, filter_value: str):
        """Set the caliber filter based on input filet value.

        Args:
            filter_value (str): filter value from config

        Raises:
            ScraperError: if an unsupported filter value is passed
        """
        if filter_value in self.supported_calibers:
            self.caliber = self.supported_calibers[filter_value]
        else:
            raise ScraperError(
                f"Caliber filter value '{filter_value}' is not supported!"
            )
        logger.debug(f"Caliber filter set to {self.caliber}")

    def _set_handedness_filter(self, filter_value: str):
        """Set the handedness filter based on input filet value.

        Args:
            filter_value (str): filter value from config

        Raises:
            ScraperError: if an unsupported filter value is passed
        """
        if filter_value in self.supported_handedness:
            self.handedness = self.supported_handedness[filter_value]
        else:
            raise ScraperError(
                f"Handedness filter value '{filter_value}' is not supported!"
            )
        logger.debug(f"Handedness filter set to {filter_value}")

    @abstractmethod
    def scrape(self) -> List[Dict[str, Union[str, int]]]:
        """Scrape the site for matching guns.

        Returns:
            List[Dict[str, Union[str, int]]]:  List of matching guns, each item
                is a dict with keys 'id', 'description','price' and 'link'
        """
