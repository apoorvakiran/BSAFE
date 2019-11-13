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
                        help='List all available projects in the Data Store. '
                             'This can help retrieve project IDs and '
                             'project names.')
    parser.add_argument('--project-id', nargs=1,
                        help='Upload data to the Data Store for'
                             'this project ID.')

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
    db.create_if_not_exist()

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

        response = create_project_in_database(db=db, team=team,
                                              project_name=project)

        if response is None:
            return

    elif args.list_available_projects:
        """
        List available buckets to upload files to. These are buckets
        from Iterate Lab's Data Store:
        """

        all_projects = db.list_all_projects()

        print("=== Listing all available projects: ===")
        print(f"Total projects in our Data Store: {len(all_projects)}.")
        print()
        for pix, pr in enumerate(all_projects):
            msg = f'   Project ({pix + 1}): ID: \'{pr["Project_ID"]}\' ' \
                  f'-- Name: \'{pr["Project_Name"]}\'.'
            logger.debug(msg)
            print(msg)

        print()

    elif args.upload:
        """
        Upload data to the Data Store. Note that Project ID needs to be
        given as well in this case.
        """
        # now get the project id to which we are uploading the data:
        if args.project_id is None:
            msg = "Please provide the Project ID for which you are uploading " \
                  "the data!\nSee help on how to get a list of " \
                  "all available IDs or on how to create a new project."
            logger.exception(msg)
            raise Exception(msg)

        # so here is the process: The data gets assigned a unique data ID
        # then it gets uploaded to S3.
        # We then also store in the Meta-Data table information about the
        # data ID and associted project ID including the link to S3 etc.
        # This was the database contains all information on what has ever
        # been uploaded by us and the data happily lives in S3:

        

        import pdb
        pdb.set_trace()

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


def get_project_id(team=None, project=None):
    """
    Construct the project ID and returns it.
    """
    proposed_project_id = team + '-' + project  # unique to this project

    return proposed_project_id


def create_project_in_database(db=None, team=None, project_name=None):
    """
    Creates a new project in the data store!

    Returns the bucket_name of the successfully created bucket and
    the randomly generated ID associated with it.
    """

    # TODO: MAKE SURE YOU CAN DO EVERYTHING YOU CAN NOW OF COURSE.
    # TODO: Security.
    # TODO: Does it show up on AWS?

    project_id = get_project_id(team=team, project=project_name)

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

    db.insert_project_if_not_exist(project_id=project_id,
                                   team_name=team, project_name=project_name,
                                   aws_access_key=aws_access_key,
                                   ip_info_token=ip_info_token,
                                   created_by_user=user_name,
                                   time_created_utc=str(datetime.datetime.utcnow()),
                                   ip=geo_tag['ip'],
                                   hostname=geo_tag['hostname'],
                                   country=geo_tag['country'],
                                   location=geo_tag['loc'],
                                   timezone=geo_tag['timezone'],
                                   created_by_system_user_name=getuser()
                                   )

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
