"""Unit tests of the TorsboGunScraper."""

from gun_scraper.scrapers.torsbo import TorsboGunScraper


def test_torsbo_gun_scraper_init__successful_instantiation():
    """Test to instantiate TorsboGunScraper with simple filters."""
    filter_dict = {"caliber": "22lr", "handedness": "left"}
    scraper = TorsboGunScraper(filter_dict)

    caliber_code_22_lr = "543"
    handedness_code_left = "8919"
    assert scraper.caliber == caliber_code_22_lr
    assert scraper.handedness == handedness_code_left
    assert scraper.query_url == (
        "https://torsbohandels.com/sv/vapen/begagnade-vapen.html?"
        f"th_kaliber={caliber_code_22_lr}&th_vanster={handedness_code_left}"
    )
