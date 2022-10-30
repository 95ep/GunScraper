"""Scraper for the site Torsbo handels."""
from typing import Dict, List, Union

from loguru import logger


from gun_scraper.scrapers.scraper_abc import GunScraperABC
from gun_scraper.utils import soup_from_url


class TorsboGunScraperError(Exception):
    """Exception to raise when something goes wrong in the Torsbo module."""

    def __init__(self, message) -> None:
        """Create the error instance and log the error message.

        Args:
            message (str): the error message to log
        """
        super().__init__(message)
        logger.error(message)


class TorsboGunScraper(GunScraperABC):
    """Scraper class for the Torsbo site."""

    base_url = "https://torsbohandels.com/sv/vapen/begagnade-vapen.html"
    supported_calibers = {"22lr": "543", "22WMR": "545", "308win": "615"}
    supported_handedness = {"left": "8919"}

    def __init__(self, filter_input: Dict[str, str]):
        """Initialize a scraper object for Torsbo.

        Args:
            filter_input (Dict[str, str]): filter settings from config
        """
        self.handedness = None
        self.caliber = None
        self._parse_filters(filter_input)
        self._build_url()

    def _set_caliber_filter(self, filter_value: str):
        """Set the caliber filter based on input filet value.

        Args:
            filter_value (str): filter value from config

        Raises:
            TorsboGunScraperError: if an unsupported filter value is passed
        """
        if filter_value in self.supported_calibers:
            self.caliber = self.supported_calibers[filter_value]
        else:
            raise TorsboGunScraperError(
                f"Caliber filter value '{filter_value}' is not supported!"
            )
        logger.debug(f"Caliber filter set to {self.caliber}")

    def _set_handedness_filter(self, filter_value: str):
        """Set the handedness filter based on input filet value.

        Args:
            filter_value (str): filter value from config

        Raises:
            TorsboGunScraperError: if an unsupported filter value is passed
        """
        if filter_value in self.supported_handedness:
            self.handedness = self.supported_handedness[filter_value]
        else:
            raise TorsboGunScraperError(
                f"Handedness filter value '{filter_value}' is not supported!"
            )
        logger.debug(f"Handedness filter set to {filter_value}")

    def _parse_filters(self, filter_input: Dict[str, str]):
        """Parse the filter input.

        Args:
            filter_input (Dict[str, str]): filter settings from config

        Raises:
            TorsboGunScraperError: if an unsupported filter key is included
                in the input
        """
        logger.debug(f"Parsing filters: {filter_input}")
        for filter_key, filter_value in filter_input.items():
            if filter_key == "handedness":
                self._set_handedness_filter(filter_value)
            elif filter_key == "caliber":
                self._set_caliber_filter(filter_value)
            else:
                raise TorsboGunScraperError(
                    f"Filter type '{filter_key}' not supported!"
                )
        logger.debug("Filters parsed")

    def _build_url(self) -> None:
        """Build the query url."""
        self.query_url = self.base_url
        url_filters = []
        if self.caliber:
            url_filters.append(f"th_kaliber={self.caliber}")
        if self.handedness:
            url_filters.append(f"th_vanster={self.handedness}")

        if url_filters:
            self.query_url += "?"
            first_filter = True
            for url_filter in url_filters:
                if not first_filter:
                    self.query_url += "&"
                self.query_url += url_filter
                first_filter = False

        logger.debug(f"URL successfully built: {self.query_url}")

    def scrape(
        self,
    ) -> List[Dict[str, Union[str, int]]]:
        """Scrape the site for matching guns.

        Returns:
            List[Dict[str, Union[str, int]]]:  List of matching guns.
        """
        soup = soup_from_url(self.query_url)
        logger.debug("Result page successfully retrieved")

        # If no gun match filter criteria, the <ol> below will be missing from page
        products_list = soup.find("ol", class_="products list items product-items row")

        matching_guns = []
        if products_list:
            logger.debug(
                "Products list <ol> tag successfully retrieved. "
                "At least one matching gun should exist"
            )
            # If no guns match filter criteria
            hits = products_list.find_all("li")
            for hit in hits:
                item_details = hit.find(
                    "div", class_="product details product-item-details"
                )
                # get item description and link
                product_item_link_raw = item_details.find(
                    "a", class_="product-item-link"
                )
                item_link = product_item_link_raw.attrs["href"]
                item_desc = product_item_link_raw.string.strip()

                # get id
                price_box = item_details.find(
                    "div", class_="price-box price-final_price"
                )
                # prepend website name to avoid collisions
                item_id = "torsbo-" + price_box.attrs["data-product-id"]

                # get price
                price_str = price_box.find("span", class_="price").string.strip()
                # strip 'kr' and blank spaces
                price_str = price_str.replace("kr", "")
                item_price = int(price_str.replace("\xa0", ""))

                matching_gun = {
                    "id": item_id,
                    "description": item_desc,
                    "price": item_price,
                    "link": item_link,
                }
                matching_guns.append(matching_gun)
                logger.debug(f"Found the following matching gun: {matching_gun}")
        else:
            logger.debug(
                "Products list <ol> tag does not exist, should mean no matching guns"
            )

        return matching_guns
