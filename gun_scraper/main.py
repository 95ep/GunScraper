from loguru import logger
from pathlib import Path
from typing import Dict, List
import yaml


import gun_scraper.file_io
import gun_scraper.notifier
import gun_scraper.scrapers.torsbo


class GunScraperError(Exception):
    def __init__(self, message) -> None:
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


@logger.catch
def main():
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
        if site == "torsbo":
            scrapers.append(
                gun_scraper.scrapers.torsbo.TorsboGunScraper(scraper_config["filters"])
            )
            logger.debug("TorsboGunScraper added to list of scrapers")
        else:
            raise GunScraperError(f"Site {site} is not supported!")

    # Call each scraper
    scraped_guns = []
    for scraper in scrapers:
        new_matches = scraper.scrape()
        if len(new_matches) > 0:
            scraped_guns.append(*new_matches)

    n_matching_guns = len(scraped_guns)
    logger.info(f"Scraping complete. {n_matching_guns} matching gun(s) found")
    logger.debug(f"The following guns were found: {scraped_guns}")

    # Filter away guns that notification has already been sent for
    data_file = Path(config["data_folder"], "data.json")
    previously_found_guns = gun_scraper.file_io.read_guns_from_file(data_file)
    new_guns = filter_scraped_guns(scraped_guns, previously_found_guns)

    # Send email
    if len(new_guns) > 0:
        gun_scraper.notifier.send_email_notification(new_guns)
    else:
        logger.info("No new guns found. No notification sent")

    gun_scraper.file_io.write_guns_to_file(scraped_guns, data_file)

    logger.info("GunScraper finished")


if __name__ == "__main__":
    main()
