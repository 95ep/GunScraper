"""Scraper for the site Jaktmarken."""
from typing import Dict, List, Union


from loguru import logger


from gun_scraper.scrapers.scraper_abc import GunScraperABC
from gun_scraper.utils import soup_from_url


class JaktmarkenScraperError(Exception):
    """Exception to raise when something goes wrong in the Jaktmarken scraper."""

    def __init__(self, message) -> None:
        """Create the error instance and log the error message.

        Args:
            message (str): the error message to log
        """
        super().__init__(message)
        logger.error(message)


class JaktmarkenGunScraper(GunScraperABC):
    """Scraper class for the Jaktmarken site."""

    _base_url = "https://www.jaktmarken.se"
    supported_calibers = {
        "22lr": "22lr-gevar-beg",
    }
    supported_handedness = {"left": "vänster"}

    def __init__(self, filter_input: Dict[str, str]):
        """Initialize a scraper object for Jaktmarken.

        Args:
            filter_input (Dict[str, str]): filter settings from config
        """
        logger.debug(
            f"Creating JaktmarkenGunScraper object with filter input {filter_input}"
        )
        self.handedness = None
        self.caliber = None
        self._parse_filters(filter_input)
        self._build_url()

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

    def _build_url(self) -> None:
        """Build the query url."""
        if self.caliber:
            self.query_url = self._base_url + "/category.html/" + self.caliber
        else:
            self.query_url = self._base_url + "/category.html/begagnade-vapen"

        logger.debug(f"URL successfully built: {self.query_url}")

    def _parse_gun_tag(self, gun_tag) -> Dict[str, Union[str, int]]:
        product_name_link_tag = gun_tag.find("div", class_="product-small-name").a

        # Extract description/title and link
        item_desc = product_name_link_tag.string
        item_link = self._base_url + product_name_link_tag["href"]

        gun_price = int(
            gun_tag.find("div", class_="product-small-price").text.split(",")[0].strip()
        )

        parsed_gun_data = {
            "id": item_desc,  # no other id than title present
            "description": item_desc,
            "price": gun_price,
            "link": item_link,
        }
        logger.debug(f"Parsed the following gun data: {parsed_gun_data}")
        return parsed_gun_data

    def scrape(
        self,
    ) -> List[Dict[str, Union[str, int]]]:
        """Scrape the site for matching guns.

        Returns:
            List[Dict[str, Union[str, int]]]:  List of matching guns, each item
                is a dict with keys 'id', 'description','price' and 'link'
        """
        matching_guns = []
        next_page_url = self.query_url

        while next_page_url:
            result_page_soup = soup_from_url(next_page_url)
            logger.debug("Result page successfully retrieved")

            gun_tags = result_page_soup.find_all(
                "li", class_="product-small product-small-vertical-small"
            )
            logger.debug(gun_tags)
            for tag in gun_tags:
                matching_guns.append(self._parse_gun_tag(tag))

            # Check if next page exists
            next_page_tag = result_page_soup.find("a", class_="button next")
            if next_page_tag:
                next_page_url = self._base_url + next_page_tag["href"]
            else:
                next_page_url = None

        if self.handedness:
            logger.debug("Handedness filter is active. Applying filter.")
            matching_guns = self._apply_handedness_filter(matching_guns)

        logger.debug(f"Found the following matching guns: {matching_guns}")
        return matching_guns
