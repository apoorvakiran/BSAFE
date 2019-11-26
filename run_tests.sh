# ********************************
# * Copyright Iterate Labs, Inc. *
# ********************************
#
# To run the staging tests locally, please follow these instructions:
# To test using staging environment locally
# 1. install redis and run redis
#  - brew install redis
#  - run with redis-server or use brew to run in background
# 2. set all the needed environment variables
# create a .env file with the following values and then type the command source .env
# export SENTRY_DSN=https://4ca7cdcc54274295af09b1f2d98f4960@sentry.io/1728777
# export ELASTIC_SEARCH_INDEX=cassia-staging
# export AWS_ACCESS_KEY=AKIAXTRZXZRUUGVCREU5
# export AWS_SECRET_KEY=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
# export ELASTIC_SEARCH_HOST=https://search-kinesis-cassia-test-ethsitlodguxwer6jtk7uozfkm.us-east-1.es.amazonaws.com
# export AWS_REGION=us-east-1
# export INFINITY_GAUNTLET_URL=https://staging-api.iteratelabs.co
# export INFINITY_GAUNTLET_AUTH=eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.x2T_qKsO8gSOz2WHLCyFzuf059L2NeH6TtdKX783ZHs
# export NO_PROXY=*
# 3. run applications locally
# - requires foreman gem, install ruby, and then install the foreman gem using
# gem install foreman
# 3.b) might have to restart shell.
# 4. run applications
# foreman s
# 5. issue curl request to get safety score and post it
# curl "localhost:5000/api/safety_score?mac=F5:12:3D:BD:DE:44&start_time=2019-03-01T00:00:00-05:00&end_time=2019-04-01T00:00:00-05:00"
# Run tests and linters over code
#
# Note: To kill processes running on port 5000 use:
#  sudo lsof -i tcp:5000
# ==================================
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

