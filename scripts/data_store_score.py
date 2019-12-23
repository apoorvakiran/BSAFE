# -*- coding: utf-8 -*-
"""This script computes the score for the latest file
for a given tester and project from Iterate Lab's Data Store.

Typical usage example:
    >> dscore --tester <tester> --project <project>

@ author Jesper Kristensen
Iterate Labs Inc. Copyright 2018-
All rights reserved
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import argparse
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import json
import pandas as pd
import sys

from ergo_analytics.data_raw import LoadDataStore
from ergo_analytics import DataFilterPipeline
from ergo_analytics.filters import FixDateOscillations
from ergo_analytics.filters import DataCentering
from ergo_analytics.filters import ConstructDeltaValues
from ergo_analytics.filters import ZeroShiftFilter
from ergo_analytics.filters import WindowOfRelevantDataFilter
from ergo_analytics.filters import DataImputationFilter
from ergo_analytics.filters import QuadrantFilter
from ergo_analytics import ErgoMetrics
from ergo_analytics import ErgoReport

ERGOMETRICS_DYNAMODB_TABLE_NAME = "ErgoMetrics"


def _put_in_database(data_id, scores):
    """Put the ErgoMetrics score information in the Dynamo DB database."""

    s3_resource = boto3.resource('dynamodb', region_name='us-east-1')
    table = s3_resource.Table(ERGOMETRICS_DYNAMODB_TABLE_NAME)

    scores_json_dumped = json.dumps(scores)

    # does the data ID already exist?
    response = table.query(KeyConditionExpression=Key('Data_ID').eq(data_id))
    exists = 'Items' in response and len(response['Items']) > 0

    if exists:
        # then we update:
        response = table.update_item(
            Key={
                'Data_ID': data_id
            },
            UpdateExpression="SET scores = list_append(scores, :i)",
            ExpressionAttributeValues={
                ':i': [scores_json_dumped],
            },
            ReturnValues="UPDATED_NEW"
        )
    else:
        # we create new:
        response = table.put_item(Item={"Data_ID": data_id,
                                        "scores": [scores_json_dumped]})

    return response['ResponseMetadata']['HTTPStatusCode'] == 200


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=('Welcome to Iterate Lab Inc.\'s '
                     'Data-Store ErgoMetric Scoring tool.'),
        epilog="Please contact 'jesper.kristensen@iteratelabs.co' "
               "if any questions.")

    parser.add_argument('--tester', required=True,
                        help='Project tester - which tester to use?')
    parser.add_argument('--project', required=True,
                        help='Project name - which project name to use?')
    parser.add_argument('--all', required=False, action='store_true',
                        help='Compute scores for all files for '
                             'this tester and project?')

    # start by parsing what the user wants to do:
    try:
        args = parser.parse_args()
    except Exception as e:
        print("Specific error = {}".format(e))
        parser.print_help()
        sys.exit(0)

    # parse the user input - selecting which tester and project to use:
    tester = args.tester
    project = args.project
    score_all = args.all

    ds = LoadDataStore()

    scores_json = dict()  # where to store final scores

    num_files = 0
    for ix, (raw_df, s3_filename) in enumerate(ds.load(tester=tester,
                                                       project=project,
                                                       all=score_all)):

        print("Computing score for file {} from {}...".format(ix + 1,
                                                              s3_filename))

        key = "{}_{}".format(ix + 1, s3_filename.replace('/', '_'))
        data_id = s3_filename

        raw_df.dropna(how='all', inplace=True)

        # make some conversions:
        raw_df.iloc[:, 0] = pd.to_datetime(raw_df.iloc[:, 0])
        for j in range(1, 6 + 1):
            raw_df.iloc[:, j] = raw_df.iloc[:, j].astype(float)

        pipeline = DataFilterPipeline()
        # instantiate the filters:
        pipeline.add_filter(name='fix_osc', filter=FixDateOscillations())
        pipeline.add_filter(name='centering1', filter=DataCentering())
        pipeline.add_filter(name='delta_values', filter=ConstructDeltaValues())
        pipeline.add_filter(name='centering2', filter=DataCentering())
        pipeline.add_filter(name='zero_shift_filter', filter=ZeroShiftFilter())
        pipeline.add_filter(name='window', filter=WindowOfRelevantDataFilter())
        pipeline.add_filter(name='impute', filter=DataImputationFilter())
        pipeline.add_filter(name='quadrant_fix', filter=QuadrantFilter())
        # run the pipeline!
        structured_data_chunks = pipeline.run(on_raw_data=raw_df,
                                              with_format_code='5',
                                              use_subsampling=False)

        metrics = ErgoMetrics(
            list_of_structured_data_chunks=structured_data_chunks)
        metrics.compute()

        # now report out the scores:
        report = ErgoReport(ergo_metrics=metrics)
        this_result = report.to_json(combine_across_data_chunks='average')

        scores_json[key] = this_result

        # append the scores
        these_scores = {str(datetime.datetime.now().utcnow().isoformat()):
                            {'result': this_result,
                             'pipeline_structure': pipeline.describe()
                             }
                        }

        response = _put_in_database(data_id, these_scores)  # update the score

    print("Scored {} files.".format(num_files))
    print("All done!")
