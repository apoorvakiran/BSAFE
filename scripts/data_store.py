#!/Users/johnjohnson/.local/share/virtualenvs/BSAFE-PHXVcO8i/bin/python
"""
This script is used to interact with Iterate Lab's Data Store.
The Data Store is an S3 bucket with all the data collected by Iterate Labs
and their wearables.

In short, the data store holds all data collected from our devices.
With this script you can create a new bucket to put data in
on the store and you can upload data to an existing bucket.

Author: Jesper Kristensen, Data Science
Copyright Iterate Labs, Inc.
"""
# Behind the scenes we use DynamoDB to keep track of all data uploaded,
# the buckets created, and so on.

import os
import sys
# == we start by finding the project root:
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.split(ROOT_DIR)[1] == 'BSAFE':
    ROOT_DIR = os.path.dirname(ROOT_DIR)  # cd ../
sys.path.insert(0, ROOT_DIR)  # now insert into our Python path
# ==

from getpass import getuser
import datetime
import logging
import argparse
import ipinfo
from constants import valid_teams
import boto3
from database import BackendDataBase

logger = logging.getLogger()

DATA_STORE_S3_BUCKET = "data-store"
DATA_STORE_DOMAIN_NAME = "DATASTORE"  # for SDB


def main():
    parser = argparse.ArgumentParser(description=('Welcome to Iterate '
                                    'Lab Inc.\'s Data-Store Tool.'
                                    'With this tool you can create new buckets '
                                    'for putting data in and add to existing '
                                    'buckets with data.'),
    epilog="Please contact 'jesper.kristensen@iteratelabs.co' "
           "if any questions.")

    # User can create new bucket
    parser.add_argument('--create-new-project', action='store_true',
                        help='Creates a new project in the Data '
                             'Store if it does not exist.')
    # User can upload data to a bucket
    parser.add_argument('--upload', nargs=1,
                        help='Upload a single file to the selected Data Store.')
    # User can upload data to a bucket
    parser.add_argument('--list-available-projects', action='store_true',
                        help='List all available projects in the Data Store.')
    parser.add_argument('--team', nargs=1,
                        help='See available projects for this team name only.')
    parser.add_argument('--project', nargs=1,
                        help='See available projects for this '
                             'project name only.')

    # start by parsing what the user wants to do:
    try:
        args = parser.parse_args()
    except Exception:
        # print help and exit:
        parser.print_help()
        return

    # make sure the backend database is created on AWS
    # (only has to be done once):
    db = BackendDataBase()
    db.create()

    if args.create_new_project:
        # Create a new project folder in our S3 Data Store:
        print("You selected to create a new project.")

        # let's first make sure the database is created in case this is the
        # first time we call this ever:

        team = input("Please enter your team name: ")
        project = input("Please enter your project name: ")
        # clean up a bit just in case:
        team = \
            team.replace(" ", "-").replace("_", "-").rstrip().lstrip().lower()

        if team not in valid_teams:
            msg = "This is not a valid team name!\n"\
                  "Please have your team registered in the database.\n"\
                  "Call this script again with --help to see email contact.\n"
            logger.exception(msg)
            raise Exception(msg)

        project = \
           project.replace(" ", "-").replace("_", "-").rstrip().lstrip().lower()

        if len(team) == 0 or len(project) == 0:
            msg = "Please provide valid team and/or project!"
            raise Exception(msg)

        response = create_project_in_database(team=team, project=project)

        if response is None:
            return

    elif args.list_available_projects:
        # List available buckets to upload files to. These are buckets
        # from Iterate Lab's Data Store:


        import pdb
        pdb.set_trace()

    elif args.upload:
        # Upload a file to an existing bucket in the Data Store:

        # when using upload, user needs to provide a bucket as well
        # to upload to:
        raise NotImplementedError("Implement me!")

    else:
        parser.print_help()
        return


def check_response(response=None):
    """
    Checks the response status when interacting with SDB.
    Raises and exception if there was an error in the response.
    """
    if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
        msg = "Error in connecting to the SDB!"
        logger.exception(msg)
        raise Exception(msg)


def get_project_id(team=None, project=None, sdb_client=None):
    """
    Construct the project ID and returns it.
    """
    proposed_project_id = team + '-' + project  # unique to this project

    # does the project ID already exist in the DB?
    query = f'SELECT * FROM {DATA_STORE_DOMAIN_NAME} WHERE ' \
            f'ProjectID = "{proposed_project_id}"'
    response = sdb_client.select(SelectExpression=query)
    check_response(response)

    if 'Items' in response:
        # we found something - so this name will not work:
        msg = "This project already exists!"
        logger.info(msg)
        print(msg)
        return

    return proposed_project_id


def create_project_in_database(team=None, project=None):
    """
    Creates a new project in the data store!

    Returns the bucket_name of the successfully created bucket and
    the randomly generated ID associated with it.
    """
    sdb = boto3.client('sdb')  # get the simple database client

    # make sure to create the DB:

    response = sdb.create_domain(DomainName=DATA_STORE_DOMAIN_NAME)
    check_response(response)

    project_id = get_project_id(team=team, project=project, sdb_client=sdb)

    if project_id is None:
        return ""

    env = os.environ
    if "IP_INFO_TOKEN" not in env:
        msg = "Please define the environment variable 'IP_INFO_TOKEN'"
        logger.exception(msg)
        raise Exception(msg)

    aws_access_key = env['AWS_ACCESS_KEY']
    ip_info_token = env["IP_INFO_TOKEN"]

    if "USER_NAME" not in env:
        msg = "Please define the user name!"
        logger.exception(msg)
        raise Exception(msg)
    user_name = env["USER_NAME"]

    handler = ipinfo.getHandler(ip_info_token)
    geo_tag = handler.getDetails().all

    # TODO:
    # CONVERT TO DYNAMO DB OVER SIMPLE DB:
    # https://gist.github.com/ikai/c79be091f98da1b709ee
    # http://boto.cloudhackers.com/en/latest/rds_tut.html
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
    # https://aws.amazon.com/dynamodb/
    # here is the Data-Store on Dynamo DB:
    # https://console.aws.amazon.com/dynamodb/home?region=us-east-1#tables:selected=Data-Store;tab=items

    # TODO: MAKE SURE YOU CAN DO EVERYTHING YOU CAN NOW OF COURSE.
    # TODO: Security.
    # TODO: Does it show up on AWS?

    # store a record in the DB about the creation of this project:
    response = sdb.put_attributes(
        DomainName=DATA_STORE_DOMAIN_NAME,
        ItemName=project_id,  # <-- unique identifier of this project
        # Store meta-data:
        Attributes=[
            {
                'Name': 'Type',
                'Value': "Project",
                'Replace': True
            },
            {
                'Name': 'ProjectID',
                'Value': project_id,
                'Replace': True
            },
            {
                'Name': 'Team_name',
                'Value': team,
                'Replace': True
            },
            {
                'Name': 'Project_name',
                'Value': project,
                'Replace': True
            },
            {
                'Name': 'IP',
                'Value': geo_tag['ip'],
                'Replace': True
            },
            {
                'Name': 'hostname',
                'Value': geo_tag['hostname'],
                'Replace': True
            },
            {
                'Name': 'country',
                'Value': geo_tag['country'],
                'Replace': True
            },
            {
                'Name': 'location',
                'Value': geo_tag['loc'],
                'Replace': True
            },
            {
                'Name': 'timezone',
                'Value': geo_tag['timezone'],
                'Replace': True
            },
            {
                'Name': 'time_created_utc',
                'Value': str(datetime.datetime.utcnow()),
                'Replace': True
            },
            {
                'Name': 'AWS_ACCESS_KEY',
                'Value': aws_access_key,
                'Replace': True
            },
            {
                'Name': 'IP_INFO_TOKEN',
                'Value': ip_info_token,
                'Replace': True
            },
            {
                'Name': 'created_by_system_user_name',
                'Value': getuser(),
                'Replace': True
            },
            {
                'Name': 'created_by_user',
                'Value': user_name,
                'Replace': True
            },
        ],
    )
    check_response(response)

    msg = f"Project ID '{project_id}' created in the Data Store!\n" \
          f"Now you can upload data to this project."
    print(msg)
    logger.debug(msg)


# def upload():
#     import pdb
#     pdb.set_trace()
#
#     max_tries = 10
#     n = 0
#     while True:
#         # keep re-creating unique ID's until good:
#         uid = generate_unique_id()  # try another random ID until we succeed
#         file_name = f"{team}/{project}/proj-data-{uid}"
#         try:
#             logger.debug(f"Trying project folder name = {file_name}")
#             upload_data_to_aws_s3(bucketname=DATA_STORE_S3_BUCKET,
#                                   filename=file_name)
#             break
#         except botocore.exceptions.ClientError:
#             msg = f"Please enter a valid project folder name and not " \
#                   f"'{file_name}'!\nCheck the team and project names!"
#             logger.exception(msg)
#             raise Exception(msg)
#         except:
#             n += 1
#             if n > max_tries:
#                 msg = "Was unable to create a new project folder under " \
#                       "'data-store' on S3!"
#                 logger.exception(msg)
#                 raise Exception(msg)
#
#     return file_name, uid

if __name__ == "__main__":
    main()
