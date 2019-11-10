# Copyright Iterate Labs, Inc.

# Run tests of the BSAFE code base in parallel over 4 workers:
pipenv run python -m pytest -v -n 4 --ignore tests/system tests tests/

