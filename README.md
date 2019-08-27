# Scientific Analytics For Ergonomics (SAFE)

This is the core data analytics platform of Iterate Labs, Inc. It contains code to parse, analyze, and reason about
data including code for generating results and insights.

The code is structured in a modern, modular, object oriented way to support rapid development, complex analyzes with
an easy interface, and straightforward ways to further develop and expand the code for developers.

<img src="data_analytics.jpg" width="450" height="240" />

## Setup
This project uses [pipenv](https://github.com/pypa/pipenv) to manage our dependencies and create a virtual environment. In order to use this project properly please install `pipenv` using the following instructions https://github.com/pypa/pipenv#installation.

You can use the commands `pipenv install` to install all of your dependencies into a virtual environment and then `pipenv shell` to enter an interactive virtual environment.

## Test
First, to ensure everything is working you will find a simple back-to-back test under "Demos".
This means a test which loads the data, sets up some key objects, and runs some
metrics as well. If that simple test runs then you should be all set.

The specific test file is called "simple_test.py". You run it with:
    >> python simple_test.py

This will help ensure that the code is running as expected after your
clone the repo. There are other tests you can run as well.
If any issues, reach out to jesper.kristensen@iteratelabs.co for help.

## Authors

+ Jesper Kristensen - Data Science Consultant
+ Jacob Tyrell - Data Scientist
+ Fnu Apoorva - CTO
+ Jason Guss - CEO

Iterate Labs Inc. - All Rights Reserved - Copyright 2018-2019
