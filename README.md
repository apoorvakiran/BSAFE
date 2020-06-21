# Behavioral and Safety Analysis for Ergonomics (BSAFE)

This is the Ergonomics arm of the data analytics & Machine Learning platform of Iterate Labs, Inc. The Data Analytics Platform (DAP) fits into the broader IoT solution (hardware, data transfer, IoT platform, etc.) of Iterate Labs and sits more specifically as part of the IoT platform.

DAP has other arms such as productivity and contact tracing - BSAFE is just one of those and contain itself a set of modules specific to ergonomics.

The code, like DAP at large, is structured in a modern, modular, object oriented way to support rapid development, complex analyzes with an easy interface, and straightforward ways to further develop and expand the code for developers.

<img src="data_analytics.jpg" width="450" height="240" />

## Larger Overview

In a larger view, BSAFE is used by the Data Lab which, in turn, uses the Data Store.
+ Link to the Data Lab: https://github.com/iteratelabs/Data_Lab
+ Link to the Data Store: https://github.com/iteratelabs/Data_Store

## Setup
Please run "source ./load_env.sh" to get set up with the appropriate BSAFE environment.

Common issues:
I don't have pipenv: This project uses [pipenv](https://github.com/pypa/pipenv) to manage our dependencies and create a virtual environment. In order to use this project properly please install `pipenv` using the following instructions https://github.com/pypa/pipenv#installation.

You can use the commands `pipenv install --dev` to install all of your development dependencies into a virtual environment and then `pipenv shell` to enter an interactive virtual environment.

Note: If you are getting errors with pipenv that it won't update and install
packages you can start fresh as follows:
+ `pipenv --rm` <-- deletes the pipenv virtual environment
+ `pipenv install --python=<path to the python exe you want to use>`

## Setup for the Flask application
In order to run the flask application you need to do two things
1. First install and run redis, this can be accomplished on a mac using homebrew
2. Install foreman, this can be done through ruby using the command `gem install ruby`. If you do not have ruby installed on your computer first install the programming language ruby.
3. Finally make sure to get a copy of the `.env` file so that you can run everything locally. Once you have created a `.env` file make sure to run `source .env` so that you have access to the values in the environment.

## Running the Flask Application
In order to run the Flask Application, you can use foreman and the command `foreman s` which will run the web server and dramtiq task queue.

## Test
We use pytest to run our tests and to make sure the BSAFE code does not regress as we build it out. The tests are part of our CI/CD integration (we use Circle CI) and run each time we push changes. The tests act as gate keepers for the deployment; we only deploy if the tests all pass. Before pushing to the repo please run the tests with `./run_tests_local.sh`.
This will go through a series of tests in the "tests/" folder in the repo. Ask the Data Science team if you have questions

## I found an Issue - How do I Report it?

Great! Thanks for checking and for helping us be even more pro-active so we can fix things before they break. Please raise an issue here and describe in as much detail as possible what you find needs more attention - or what you find should be improved or even developed as a new feature. Just tag a Data Science team member and we will be in touch. Thanks for helping us improve BSAFE!

## How to Contribute to the Code Base

Feel free to pull this code, make changes, make sure the tests pass and then raise a pull request on Github and a team member from the Data Science team will review. Please review this if you're unsure of this process flow: https://iteratelabs.atlassian.net/wiki/spaces/CP/pages/36077642/Typical+Git+workflow

## Owning Team

The Data Science team at Iterate Labs owns BSAFE. Please reach out to the data science team at jesper.kristensen@iteratelabs.co for questions/comments/suggestions.

## Authors

+ Jesper Kristensen (Data Scientist)
+ Fnu Apoorva (Chief Technology Officer)
+ Jason Guss (Chief Executive Officer)

## BSAFE Alumni
+ James Russo (Software Engineer)

Iterate Labs Inc. - All Rights Reserved - Copyright 2018-2019 - Patent Pending
