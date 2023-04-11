# Build GunScraper

1. Verify that QA is passing, `./ci/qa.sh`
1. Bump version using `bumpver` and merge to master, e.g. `bumpver update --minor`. Make sure a tag is created.
1. Build using `poetry`: `poetry build`
1. Publish to PyPi: `poetry publish`