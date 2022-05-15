from typing import Dict, List, Union

from abc import ABC, abstractmethod

# TODO: Check which of these classes maybe should be concrete instead


class GunScraperABC(ABC):
    @abstractmethod
    def __init__(self, filters: Dict[str, str]):
        """_summary_

        Args:
            filters (Dict[str, str]): _description_
        """

    @abstractmethod
    def _parse_filters(self, filters: Dict[str, str]):
        """_summary_

        Args:
            filters (Dict[str, str]): _description_
        """

    @abstractmethod
    def _set_caliber_filter(self, filter_value: str):
        """_summary_

        Args:
            filter_value (str): _description_

        Raises:
            NotImplementedError: _description_
        """

    @abstractmethod
    def _set_handedness_filter(self, filter_value: str):
        """_summary_

        Args:
            filter_value (str): _description_
        """

    @abstractmethod
    def scrape(self) -> List[Dict[str, Union[str, int]]]:
        """Scrape the site for matching guns.

        Returns:
            List[Dict[str, Union[str, int]]]:  List of matching guns, each item is a dict
                with keys 'id', 'description','price' and 'link'
        """
