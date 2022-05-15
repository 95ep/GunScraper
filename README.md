# GunScraper

## Setup

1. Create a `config.yaml` at the root of the repo based on `config_template.yaml`.
1. Add Cron Job to run `runner.sh` at desired interval.

Example Cron Job:

```
* */12 * * * <path-to-repo>/GunScraper/runner.sh >/tmp/stdout.log 2>/tmp/stderr.log
```
