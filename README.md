# Behavioral and Safety Analysis for Ergonomics (BSAFE)

This is the core data analytics & Machine Learning platform of Iterate Labs, Inc. It contains code to parse, analyze, and reason about
data including code for generating results and insights.

The code is structured in a modern, modular, object oriented way to support rapid development, complex analyzes with
an easy interface, and straightforward ways to further develop and expand the code for developers.

<img src="data_analytics.jpg" width="450" height="240" />

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
We use pytest to run our tests. Before pushing to the repo please run the tests with ./run_tests.sh.
This will go through a set of tests in the "tests/" folder in the repo.

## Authors

+ Jesper Kristensen (Data Scientist)
+ Fnu Apoorva (Chief Technology Officer)
+ Jason Guss (Chief Executive Officer)

## BSAFE Alumni
+ James Russo (Software Engineer)

Iterate Labs Inc. - All Rights Reserved - Copyright 2018-2019 - Patent Pending
