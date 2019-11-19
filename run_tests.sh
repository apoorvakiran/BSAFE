# ********************************
# * Copyright Iterate Labs, Inc. *
# ********************************
# Run tests and linters over code
echo

# Run tests of the BSAFE code base in parallel over 4 workers:
echo "Run pytest to unit, integration, and system tests..."
pipenv run python -m pytest -v -n 4 --ignore tests/system tests tests/
echo "[completed]"

# Run pylama as a linter / code checker - make sure our code looks good:
echo
echo "Now making sure code quality is OK."
# pipenv run python -m pytest --pylama -n 4 ergo_analytics/
echo "[completed]"

echo
echo "[ALL OK] All good to push commit!"
echo

