# GunScraper

A simple scraper for finding guns, according to search criteria, from Swedish gun shops.

Currently three shops are supported: 

* [Torsbo Handels](https://torsbohandels.com/) 
* [JG Jakt](https://www.jgjakt.se/)
* [Jaktmarken.se/Marks Jakt och Fiskecenter](https://www.jaktmarken.se)

## Setup

In order to install and setup GunScraper, follow the steps below:

1. Create a virtual environment
1. Install GunScraper and dependencies: `pip install gun_scraper`
1. Download the configuration template `misc/config.yaml`
1. Update the configuration
1. Download `misc/runner.sh` and edit it with the path to the virtual environment
  and config file
1. Create a Cron Job to run `runner.sh` at desired interval

Example Cron Job, running every 12th hour:
```
0 */12 * * * <path-to-repo>/GunScraper/runner.sh >/tmp/stdout.log 2>/tmp/stderr.log
```

## Config

The `config.yaml` follows the following syntax:

```yaml
scraper:
  filters:
    # Dictionary defining which filters to apply
    caliber: # Possible values: 22lr, 22WMR or 308win
    handedness: # Possible values: left
  sites:
    - # List defining which sites to scrape. Supported values: 'torsbo', 'jg' and 'jaktmarken'

email:
  sender: # email address that will appear as sender of the notification emails
  receiver: # email that will receive notification emails
  smtp_server: # hostname of smtp server used to send notifications
  ssl_port: # SSL port of the 'smtp_server'
  username: # username for the 'smtp_server'
  password: # password for the 'smtp_server'
  alive_msg_interval: # interval (in hours) to send notification in case no guns matching search criteria is found

data_folder: # folder to store persistent data in
logs_folder: # folder to store log output in
```