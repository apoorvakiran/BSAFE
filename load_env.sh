# Copyright Iterate Labs, Inc.

# Set up the virtual environment from the pipfile:
# (see the Pipfile and Pipfile.lock):
pipenv shell

# Token for API calls to get geo-location when uploading data:
# we use https://ipinfo.io for this
# note: Free usage of our API is limited to 50,000 API requests per month. If you exceed that limit we'll return a 429 HTTP status code to you.
# This should more than cover us by a lot, but just note this if we do
# get the 429 error.
export IP_INFO_TOKEN=77e263a113d398
