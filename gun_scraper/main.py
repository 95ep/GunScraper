"""Module containing the main functionality of GunScraper."""
from pathlib import Path
import time
from typing import Dict, List

from loguru import logger
import yaml

from gun_scraper.file_io import (
    read_guns_from_file,
    read_notification_timestamp_from_file,
    write_guns_to_file,
    write_notification_timestamp_to_file,
)
from gun_scraper.notifier import send_alive_notification, send_gun_notification
from gun_scraper.scrapers.jg import JGGunScraper
from gun_scraper.scrapers.torsbo import TorsboGunScraper


class GunScraperError(Exception):
    """Custom error class for GunScraper."""

    def __init__(self, message: str) -> None:
        """Create error instance and log error message.

        Args:
            message (str): message to include in error
        """
        super().__init__(message)
        logger.error(message)


def filter_scraped_guns(scraped_guns: List[Dict], old_guns: List[Dict]) -> List[Dict]:
    """Filter out guns that notification already has been sent for.

    Args:
        scraped_guns (List[Dict]): list of guns found in this round of scraping
        old_guns (List[Dict]): list of guns found in previous rounds of scraping

    Returns:
        List[Dict]: list of guns not previously found
    """
    ids_old_guns = [gun["id"] for gun in old_guns]
    new_guns = [gun for gun in scraped_guns if gun["id"] not in ids_old_guns]
    logger.info(f"Filtering complete. The following new guns were found: {new_guns}")
    return new_guns


def check_latest_notification(alive_notification_interval: int, data_file: Path):
    """Check time since latest notification and send alive notification if needed.

    Args:
        alive_notification_interval (int): Maximum interval, in hours, between
            notifications
        data_file (Path): path to file holding scraped guns
    """
    timestamp = read_notification_timestamp_from_file(data_file)
    hours_since_notification = (time.time() - timestamp) / 3600
    logger.debug(f"Sending notification every {alive_notification_interval} hours.")

    # Send notification if notification interval has elapsed
    if hours_since_notification > alive_notification_interval:
        logger.info(
            f"{hours_since_notification} hours elapsed since last notification, "
            "sending notification!"
        )
        send_alive_notification()
        write_notification_timestamp_to_file(data_file)
    else:
        logger.debug(
            f"{hours_since_notification} hours elapsed since last notification, "
            "not sending notification!"
        )


@logger.catch
def main():
    """Execute one round of scraping.

    Raises:
        GunScraperError: if a unsupported site is included in the config
    """
    # Run the entire process of scraping, sending email etc here
    # Add log sink
    logger.add(Path("logs", "gun_scraper-{time}.log"), retention="30 days")
    logger.info("GunScraper started")

    # Load some config file
    config_file_path = Path("config.yaml")
    with open(config_file_path) as f:
        config = yaml.safe_load(f)
    scraper_config = config["scraper"]
    logger.debug(f"The following config is read: {config}")

    # Create list of scrapers to use
    scrapers = []
    for site in scraper_config["sites"]:
        filter_config = scraper_config["filters"]
        if site == "torsbo":
            scrapers.append(TorsboGunScraper(filter_config))
            logger.debug("TorsboGunScraper added to list of scrapers")
        elif site == "jg":
            scrapers.append(JGGunScraper(filter_config))
            logger.debug("JGGunScraper added to list of scrapers")
        else:
            raise GunScraperError(f"Site {site} is not supported!")

    # Call each scraper
    scraped_guns = []
    for scraper in scrapers:
        new_matches = scraper.scrape()
        if len(new_matches) > 0:
            scraped_guns.extend(new_matches)

    n_matching_guns = len(scraped_guns)
    logger.info(f"Scraping complete. {n_matching_guns} matching gun(s) found")
    logger.debug(f"The following guns were found: {scraped_guns}")

    # Filter away guns that notification has already been sent for
    data_file = Path(config["data_folder"], "data.json")
    previously_found_guns = read_guns_from_file(data_file)
    new_guns = filter_scraped_guns(scraped_guns, previously_found_guns)

    # Send email
    if len(new_guns) > 0:
        send_gun_notification(new_guns)
        write_notification_timestamp_to_file(data_file)
    else:
        logger.info("No new guns found. No notification sent")
        # Check if alive notification should be sent
        check_latest_notification(config["email"]["alive_msg_interval"], data_file)

    write_guns_to_file(scraped_guns, data_file)

    logger.info("GunScraper finished")


if __name__ == "__main__":
    main()
