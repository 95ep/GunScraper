"""Unit tests of the JGGunScraper."""

from gun_scraper.scrapers.jg import JGGunScraper


def test_jg_gun_scraper_init__successful_instantiation():
    """Test to instantiate JGGunScraper with simple filters."""
    filter_dict = {"caliber": "22lr", "handedness": "left"}
    scraper = JGGunScraper(filter_dict)

    caliber_code_22_lr = "22lr-56x15r"
    assert scraper.caliber == caliber_code_22_lr
    assert scraper.handedness == "vänster"
    assert scraper.query_url == (
        "https://www.jgjakt.se/product-category/vapen/begagnade-vapen/?"
        f"pa_kaliber={caliber_code_22_lr}"
    )
