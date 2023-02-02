#!/bin/bash
# Change working dir to script folder
script_folder=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$script_folder"

venv_path=<Enter path to virtual environment>
source ${venv_path}/bin/activate
config_file=<Enter path to config file>
gun_scraper -c ${config_file}
deactivate
