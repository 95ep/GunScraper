# GunScraper

## Setup

1. Create a `config.yaml` at the root of the repo based on `config_template.yaml`.
1. Create a Python3 virtual environment named `.venv` in the root of the repo
1. Add Cron Job to run `runner.sh` at desired interval.

Example Cron Job:

```
0 */12 * * * <path-to-repo>/GunScraper/runner.sh >/tmp/stdout.log 2>/tmp/stderr.log
```

## Improvements list

1. Logging to file
1. Install requirements as part of Shell-script
1. Keep track of which guns notfications has already been sent for
1. Add support for additional sites
    1. Marks JoF/Vildmarken.se
    1. JG Jakt
    1. Wildmark Ullared