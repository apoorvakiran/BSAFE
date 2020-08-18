# -*- coding: utf-8 -*-
"""Responsible for setting up the BSAFE job run based on given input from the user.

Typically in the form of a YAML file that is parsed and sent to the functions below.

@ author Jesper Kristensen
Copyright 2018 Iterate Labs, Inc.
All Rights Reserved. Patent pending.
"""

import hashlib
import json
import git
import yaml
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import *  # used via an "exec" call later
from ergo_analytics.metrics import *

__all__ = ["parse_bsafe_yaml", "construct_datafilter_pipeline", "construct_metrics"]

BSAFE_PATH = "."


def construct_datafilter_pipeline(scoring_definition=None):
    """Construct data filter pipeline."""
    global pipeline
    pipeline = DataFilterPipeline()
    if "filters" in scoring_definition["data_pipeline"]:
        for this_filter in scoring_definition["data_pipeline"]["filters"]:
            try:
                exec(
                    'global pipeline; pipeline.add_filter(filter={}(), name="{}")'.format(
                        this_filter["type"], this_filter["type"]
                    )
                )
            except NameError as e:
                msg = "Please import the filter '{}' into experiment.py (exact error: '{}')".format(
                    this_filter["type"], e
                )
                raise NameError(msg)

            if "params" in this_filter and len(this_filter["params"]) > 0:
                pipeline.update_filter(
                    name=this_filter["type"], new_params=this_filter["params"]
                )

    return pipeline


def construct_metrics(scoring_definition=None):
    """Construct metrics."""
    global metrics
    parameters = dict()
    metrics = dict()
    for metric in scoring_definition["metrics"]:
        parameters[metric] = scoring_definition["metrics"][metric]
        exec('global metrics; metrics["{}"] = {}'.format(metric, metric))

    if len(metrics) == 0:
        raise ValueError("Please provide at least 1 metric to compute!")

    return metrics, parameters


def get_bsafe_revision():
    """Return the current bsafe hash"""
    try:
        repo = git.Repo(BSAFE_PATH)
        sha = repo.head.object.hexsha  # commit sha of HEAD
        assert sha is not None
    except Exception:
        # can happen in deployment
        sha = "n/a"
    return sha


def parse_bsafe_yaml(yamlfile=None):
    """Scoring definition file: How should the scoring be carried out?"""

    options = dict()
    m = hashlib.sha256()
    m.update(json.dumps(options).encode())

    # Make sure that the BSAFE revision factors into the scoring hash explicitly:
    bsafe_revision = get_bsafe_revision()  # new revision: New scoring hash, always.
    m.update(bsafe_revision.encode())

    if yamlfile is None:
        # nothing to do
        return options, m.hexdigest()

    try:
        with open(yamlfile) as f:
            definitions = yaml.load(f, Loader=yaml.FullLoader)
        definitions = definitions["scoring_definition"]

        if "bsafe_revision" in definitions:
            # we already accounted for this in the hash
            del definitions["bsafe_revision"]

        if "force_rerun" in definitions:
            del definitions["force_rerun"]  # don't let this take part in the hash

    except Exception as e:
        print("Error loading Yaml file!")
        print("The error is: {}".format(e))
        return options, m.hexdigest()

    if len(definitions) > 0:
        options.update(**definitions)

    m = hashlib.sha256()
    m.update(json.dumps(options).encode())

    _validate(scoring_definition=options)

    return options, m.hexdigest()


def _validate(scoring_definition):
    """Validate the pipeline structure."""

    if "data_pipeline" not in scoring_definition:
        raise Exception("Please define the data pipeline in the definition file!")
