#!/bin/bash
set -e

black --check gun_scraper tests
flake8 gun_scraper tests
pytest tests
