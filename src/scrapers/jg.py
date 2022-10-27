"""Scraper for the site JG Jakt."""
from typing import Dict, List, Union


from loguru import logger


from gun_scraper.scrapers.scraper_abc import GunScraperABC
from gun_scraper.utils import soup_from_url


class JGScraperError(Exception):
    """Exception to raise when something goes wrong in the JG module."""

    def __init__(self, message) -> None:
        """Create the error instance and log the error message.

        Args:
            message (str): the error message to log
        """
        super().__init__(message)
        logger.error(message)


class JGGunScraper(GunScraperABC):
    """Scraper class for the JG Jakt site."""

    _base_url = "https://www.jgjakt.se/product-category/vapen/begagnade-vapen/"
    supported_calibers = {
        "22lr": "22lr-56x15r",
        "22WMR": "22-wmr-56x26r",
        "308win": "308-win-762x51",
    }
    supported_handedness = {"left": "vänster"}

    def __init__(self, filter_input: Dict[str, str]):
        """Initialize a scraper object for Torsbo.

        Args:
            filter_input (Dict[str, str]): filter settings from config
        """
        logger.debug(f"Creating JGGunScraper object with filter input {filter_input}")
        self.handedness = None
        self.caliber = None
        self._parse_filters(filter_input)
        self._build_url()

    def _set_caliber_filter(self, filter_value: str):
        """Set the caliber filter based on input filet value.

        Args:
            filter_value (str): filter value from config

        Raises:
            JGScraperError: if an unsupported filter value is passed
        """
        if filter_value in self.supported_calibers:
            self.caliber = self.supported_calibers[filter_value]
        else:
            raise JGScraperError(
                f"Caliber filter value '{filter_value}' is not supported!"
            )
        logger.debug(f"Caliber filter set to {self.caliber}")

    def _set_handedness_filter(self, filter_value: str):
        """Set the handedness filter based on input filet value.

        Args:
            filter_value (str): filter value from config

        Raises:
            JGScraperError: if an unsupported filter value is passed
        """
        if filter_value in self.supported_handedness:
            self.handedness = self.supported_handedness[filter_value]
        else:
            raise JGScraperError(
                f"Handedness filter value '{filter_value}' is not supported!"
            )
        logger.debug(f"Handedness filter set to {filter_value}")

    def _apply_handedness_filter(
        self, found_guns: List[Dict[str, Union[str, int]]]
    ) -> List[Dict[str, Union[str, int]]]:
        """Filter guns based on handedness.

        Heuristic filtering by checking keywords for the handedness
        is present in the description

        Args:
            found_guns (List[Dict[str, Union[str, int]]]): list of guns
                found when scraping

        Returns:
            List[Dict[str, Union[str, int]]]: guns matching the handedness criteria
        """
        logger.debug(
            f"Applying the following handedness filter value: {self.handedness}"
        )
        guns_matching_handedness = []
        # Check if handedness keyword is present in description
        for gun in found_guns:
            if self.handedness in gun["description"].lower():
                logger.debug(f"The following gun matches the handedness filter:\n{gun}")
                guns_matching_handedness.append(gun)
            else:
                logger.debug(
                    f"The following gun doesn't match the handedness filter:\n{gun}"
                )

        return guns_matching_handedness

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
            if filter_key == "handedness":
                self._set_handedness_filter(filter_value)
            elif filter_key == "caliber":
                self._set_caliber_filter(filter_value)
            else:
                raise JGScraperError(f"Filter type '{filter_key}' not supported!")
        logger.debug("Filters parsed")

    def _build_url(self) -> None:
        """Build the query url."""
        self.query_url = self._base_url
        url_filters = []
        if self.caliber:
            url_filters.append(f"pa_kaliber={self.caliber}")

        if url_filters:
            self.query_url += "?"
            first_filter = True
            for url_filter in url_filters:
                if not first_filter:
                    self.query_url += "&"
                self.query_url += url_filter
                first_filter = False

        logger.debug(f"URL successfully built: {self.query_url}")

    def _parse_gun_data(self, gun_tags: List) -> List[Dict[str, Union[str, int]]]:
        """Parse the data for each gun from the list of gun tags.

        Args:
            gun_tags (List): List with tags for each gun found

        Returns:
            List[Dict[str, Union[str, int]]]: List of guns, each item
                is a dict with keys 'id', 'description','price' and 'link'
        """
        gun_list = []
        for gun_tag in gun_tags:
            post_data_inner_tag = gun_tag.find("div", class_="post_data_inner")

            post_data_price_tag = post_data_inner_tag.find(
                "div", class_="post_data_price"
            )

            # Extract price, price string is on format '35,000kr'
            price_str = post_data_price_tag.find("bdi").text.strip()
            # Remove decimal comma
            price_str = price_str.replace(",", "")
            # Remove 'kr' and cast to int
            gun_price = int(price_str.replace("kr", ""))

            # The add to chart <a> tag contains the product id in it's attributes
            add_to_chart_link = post_data_price_tag.find("a", {"data-product_id", True})
            gun_id = add_to_chart_link.attrs["data-product_id"]

            # Get the <a> tag containing href and desc
            post_a_tag = post_data_inner_tag.find(
                "div", class_="post_header entry-header"
            ).h2.a
            item_desc = post_a_tag.string
            item_link = post_a_tag.attrs["href"]

            parsed_gun_data = {
                "id": gun_id,
                "description": item_desc,
                "price": gun_price,
                "link": item_link,
            }
            logger.debug(f"Parsed the following gun data: {parsed_gun_data}")
            gun_list.append(parsed_gun_data)

        return gun_list

    def scrape(
        self,
    ) -> List[Dict[str, Union[str, int]]]:
        """Scrape the site for matching guns.

        Returns:
            List[Dict[str, Union[str, int]]]:  List of matching guns, each item
                is a dict with keys 'id', 'description','price' and 'link'
        """
        result_page_soup = soup_from_url(self.query_url)
        logger.debug("Result page successfully retrieved")

        # If no gun match url filter, the <ul> below will be missing from page
        gun_list_tag = result_page_soup.find("ul", class_="products columns-2")

        matching_guns = []
        if gun_list_tag:
            gun_tags = []
            next_page = True
            # Browse through all pages with hits
            while next_page:
                # Extract all gun tags from the list of the current page
                gun_tags.extend(gun_list_tag.find_all("li"))
                # Check if there is additional pages with hits
                next_page = result_page_soup.find("a", class_="next page-numbers")
                # Load the next page and extract the gun list tag
                if next_page:
                    logger.debug("Another page with results exists")
                    result_page_soup = soup_from_url(next_page.attrs["href"])
                    gun_list_tag = result_page_soup.find(
                        "ul", class_="products columns-2"
                    )
            matching_guns = self._parse_gun_data(gun_tags)

            if self.handedness:
                logger.debug("Handedness filter is active. Applying filter.")
                matching_guns = self._apply_handedness_filter(matching_guns)

            logger.debug(f"Found the following matching guns: {matching_guns}")

        else:
            logger.debug(
                "Products list <ul> tag does not exist, should mean no matching guns"
            )

        return matching_guns
