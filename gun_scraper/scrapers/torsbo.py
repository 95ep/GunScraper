from typing import Dict, List, Union

import requests
from bs4 import BeautifulSoup

from gun_scraper.scrapers.scraper_abc import GunScraperABC


class TorsboGunScraperError(Exception):
    # Add some logging logic here, loguru??
    pass


class TorsboGunScraper(GunScraperABC):
    base_url = "https://torsbohandels.com/sv/vapen/begagnade-vapen.html"
    supported_calibers = {"22lr": "543", "22WMR": "545", "308win": "615"}
    supported_handedness = {"left": "8919"}

    def __init__(self, filters: Dict[str, str]):
        self.handedness = None
        self.caliber = None
        self._parse_filters(filters)
        self._build_url()

    def _set_caliber_filter(self, filter_value: str):
        if filter_value in self.supported_calibers:
            self.caliber = self.supported_calibers[filter_value]
        else:
            raise TorsboGunScraperError(
                f"Caliber filter value '{filter_value}' is not supported!"
            )

    def _set_handedness_filter(self, filter_value: str):
        if filter_value in self.supported_handedness:
            self.handedness = self.supported_handedness[filter_value]
        else:
            raise TorsboGunScraperError(
                f"Handedness filter value '{filter_value}' is not supported!"
            )

    def _parse_filters(self, filters: Dict[str, str]):
        """_summary_

        Args:
            filters (Dict[str, str]): _description_

        Raises:
            TorsboGunScraperError: _description_
        """
        for filter_key, filter_value in filters.items():
            if filter_key == "handedness":
                self._set_handedness_filter(filter_value)
            elif filter_key == "caliber":
                self._set_caliber_filter(filter_value)
            else:
                raise TorsboGunScraperError(
                    f"Filter type '{filter_key}' not supported!"
                )

    def _build_url(self) -> None:
        """_summary_"""
        self.query_url = self.base_url
        url_filters = []
        if self.caliber:
            url_filters.append(f"th_kaliber={self.caliber}")
        if self.handedness:
            url_filters.append(f"th_vanster={self.handedness}")

        if url_filters:
            self.query_url += "?"
            for url_filter in url_filters:
                self.query_url += url_filter + "&"

    def scrape(
        self,
    ) -> List[Dict[str, Union[str, int]]]:
        """Scrape the site for matching guns

        Returns:
            List[Dict[str, Union[str, int]]]:  List of matching guns.
        """
        result_page = requests.get(self.query_url)
        soup = BeautifulSoup(result_page.content, "html.parser")

        # If no gun match filter criteria, the <ol> below will be missing from page
        products_list = soup.find("ol", class_="products list items product-items row")
        matching_guns = []
        if products_list:
            # If no guns match filter criteria
            hits = products_list.find_all("li")
            matching_guns = []
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
                # prepend website name to avoid collisons
                item_id = "torsbo-" + price_box.attrs["data-product-id"]

                # get price
                price_str = price_box.find("span", class_="price").string.strip()
                # strip 'kr' and blankspace
                price_str = price_str.replace("kr", "")
                item_price = int(price_str.replace("\xa0", ""))

                matching_guns.append(
                    {
                        "id": item_id,
                        "description": item_desc,
                        "price": item_price,
                        "link": item_link,
                    }
                )

        return matching_guns
