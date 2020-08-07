# ********************************
# * Copyright Iterate Labs, Inc. *
# ********************************

echo

# Run tests of the Data Store code base in parallel over 4 workers:
echo "Run pytest to unit, integration, and system tests..."
pipenv run python -m pytest -nauto tests/ --pdb
# echo "[completed]"

# Run pylama as a linter / code checker - make sure our code looks good:
#echo
#echo "Now making sure code quality is OK."
# python -m pytest --pylama -n 4 ergo_analytics/
#echo "[completed]"

#echo
#echo "[ALL OK] All good to push commit!"
#echo
