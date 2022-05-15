#!/bin/bash
# Chang working dir to repo root
repo_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$repo_path"
source .venv/bin/activate

# Add repo root to PYTHONPATH so root user find
# the package
export PYTHONPATH=$repo_path

python gun_scraper/main.py
deactivate
echo "Shell script done"