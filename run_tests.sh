# Copyright Iterate Labs, Inc.

# Run pylama as a linter / code checker:
pylama --sort E,W,D ergo_analytics/

# Now run tests of the BSAFE code base in parallel over 4 workers:
pipenv run python -m pytest -v -n 4 --ignore tests/system tests tests/

