from loguru import logger
from pathlib import Path
import yaml

from gun_scraper.notifier import send_email_notification
from gun_scraper.scrapers.torsbo import TorsboGunScraper


class GunScraperError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)
        logger.error(message)


@logger.catch
def gun_scraper():
    # Run the entire process of scraping, sending email etc here
    # Add log sink
    logger.add(Path("logs", "gun_scraper-{time}.log"), retention="30 days")
    logger.info("GunScraper started")

    # Load some config file
    config_file_path = Path("config.yaml")
    with open(config_file_path) as f:
        config = yaml.safe_load(f)
    scraper_config = config["scraper"]
    logger.debug(f"The following scraper config is read: {scraper_config}")

    # Create list of scrapers to use
    scrapers = []
    for site in scraper_config["sites"]:
        if site == "torsbo":
            scrapers.append(TorsboGunScraper(scraper_config["filters"]))
            logger.debug("TorsboGunScraper added to list of scrapers")
        else:
            raise GunScraperError(f"Site {site} is not supported!")

    # Call each scraper
    matching_guns = []
    for scraper in scrapers:
        new_matches = scraper.scrape()
        if len(new_matches) > 0:
            matching_guns.append(*new_matches)

    n_matching_guns = len(matching_guns)
    logger.info(f"Scraping complete. {n_matching_guns} matching gun(s) found")
    logger.debug(f"The following guns were found: {matching_guns}")

    # TODO: Put which items has been found in some file to avoid duplicates

    # Send email
    if n_matching_guns > 0:
        send_email_notification(matching_guns)

    logger.info("GunScraper finished")


if __name__ == "__main__":
    gun_scraper()
