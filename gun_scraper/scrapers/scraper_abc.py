"""Abstract base class all site scraper should inherit."""
from abc import ABC, abstractmethod
from typing import Dict, List, Union


# TODO: Check which of these methods maybe should be concrete instead


class GunScraperABC(ABC):
    """Abstract class for all site scrapers."""

    @abstractmethod
    def __init__(self, filter_input: Dict[str, str]):
        """Create the scraper object.

        Args:
            filter_input (Dict[str, str]): filter settings from config
        """

    @abstractmethod
    def _parse_filters(self, filter_input: Dict[str, str]):
        """Parse the filter input.

        Args:
            filter_input (Dict[str, str]): filter settings from config
        """

    @abstractmethod
    def _set_caliber_filter(self, filter_value: str):
        """Set the value for the caliber filter.

        Args:
            filter_value (str): value of the caliber filter
        """

    @abstractmethod
    def _set_handedness_filter(self, filter_value: str):
        """Set the value for the handedness filter.

        Args:
            filter_value (str): value of the handedness filter
        """

    @abstractmethod
    def scrape(self) -> List[Dict[str, Union[str, int]]]:
        """Scrape the site for matching guns.

        Returns:
            List[Dict[str, Union[str, int]]]:  List of matching guns, each item
                is a dict with keys 'id', 'description','price' and 'link'
        """
