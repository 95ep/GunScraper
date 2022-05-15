from pathlib import Path
import yaml

from gun_scraper.notifier import send_email_notification
from gun_scraper.scrapers.torsbo import TorsboGunScraper


class GunningForGunsError(Exception):
    # Add some logging logic here, loguru??
    pass


def gunning_for_guns():
    # Run the entire process of scraping, sending email etc here

    # Load some config file
    with open(Path("config.yaml")) as f:
        config = yaml.safe_load(f)
    scraper_config = config["scraper"]

    # Create list of scrapers to use
    scrapers = []
    for site in scraper_config["sites"]:
        if site == "torsbo":
            scrapers.append(TorsboGunScraper(scraper_config["filters"]))
        else:
            raise GunningForGunsError(f"Site {site} is not supported!")

    # Call each scraper
    matching_guns = []
    for scraper in scrapers:
        new_matches = scraper.scrape()
        matching_guns.append(*new_matches)

    # TODO: Put which items has been found in some file to avoid duplicates

    # Send email
    if len(matching_guns) > 0:
        send_email_notification(matching_guns)

    print("Gunning for Guns finished")


if __name__ == "__main__":
    gunning_for_guns()
