#!/Users/johnjohnson/.local/share/virtualenvs/BSAFE-PHXVcO8i/bin/python
"""
This script is used to interact with Iterate Lab's data store.

In short, the data store holds all data collected from our devices.
With this script you can create a new bucket to put data in
on the store and you can upload data to an existing bucket.

Author: Jesper Kristensen, Data Science
Copyright Iterate Labs, Inc.
"""
# Behind the scenes we use DynamoDB to keep track of all data uploaded,
# the buckets created, and so on.

import os
import datetime
import logging
import argparse
import ipinfo
from constants import valid_teams
from constants import generate_unique_id
from ergo_analytics.data_raw import upload_data_to_aws_s3
import boto3
import botocore

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
                        help='Creates a project in the Data Store.')
    # User can upload data to a bucket
    parser.add_argument('--upload', nargs=1,
                        help='Upload a single file to the Data Store.')
    # User can upload data to a bucket
    parser.add_argument('--list-available-projects', action='store_true',
                        help='See available buckets.')
    parser.add_argument('--team', nargs=1,
                        help='See available buckets for this team only.')
    parser.add_argument('--project-name', nargs=1,
                        help='See available buckets for this project only.')

    # start by parsing what the user wants to do:
    try:
        args = parser.parse_args()
    except Exception:
        # print help and exit:
        parser.print_help()
        return

    if args.create_new_project:
        # Create a new project folder in our S3 Data Store:
        print("You selected to create a new project.")

        team = input("Please enter your team name: ")

        # TODO: Check for existing project names
        # project = None
        # while not project_name_is_valid(project):
        project = input("Please enter your project name: ")

        # clean up:
        team = team.replace(" ", "-").replace("_", "-")
        project = project.replace(" ", "-").replace("_", "-")

        bucketname, uid = create_project_in_database(team=team, project=project)

        # now store in SDB what happened:


        import pdb
        pdb.set_trace()



        msg = f"Bucket successfully created in the Data Store: " \
              f"'{bucketname}'!\nThe ID is {uid}."
        logger.info(msg)
        print(msg)

    elif args.get_available_projects:
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


def project_name_is_valid(project_name=None):
    """
    Check that this project name can be used.
    """

    import pdb
    pdb.set_trace()


def check_response(response=None):
    """
    Checks the response when interacting with SDB.
    """
    if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
        msg = "Error in connecting to the SDB!"
        logger.exception(msg)
        raise Exception(msg)


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

    project_id = team + '-' + project  # unique to this project

    env = os.environ
    if "IP_INFO_TOKEN" not in env:
        msg = "Please define the environment variable 'IP_INFO_TOKEN'"
        logger.exception(msg)
        raise Exception(msg)

    handler = ipinfo.getHandler(env["IP_INFO_TOKEN"])
    geo_tag = handler.getDetails().all

    # store a record in the DB about the creation of this project:
    response = sdb.put_attributes(
        DomainName=DATA_STORE_DOMAIN_NAME,
        ItemName=project_id,
        Attributes=[
            {
                'Name': 'Team',
                'Value': team,
                'Replace': True
            },
            {
                'Name': 'Project',
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
                'Value': datetime.datetime.utcnow(),
                'Replace': True
            },
        ],
    )
    check_response(response)

    # response = sdb.select(SelectExpression=f'select * from {DATA_STORE_DOMAIN_NAME} where Team = "data-science"')

    max_tries = 10
    n = 0
    while True:
        # keep re-creating unique ID's until good:
        uid = generate_unique_id()  # try another random ID until we succeed
        file_name = f"{team}/{project}/proj-data-{uid}"
        try:
            logger.debug(f"Trying project folder name = {file_name}")
            upload_data_to_aws_s3(bucketname=DATA_STORE_S3_BUCKET,
                                  filename=file_name)
            break
        except botocore.exceptions.ClientError:
            msg = f"Please enter a valid project folder name and not " \
                  f"'{file_name}'!\nCheck the team and project names!"
            logger.exception(msg)
            raise Exception(msg)
        except:
            n += 1
            if n > max_tries:
                msg = "Was unable to create a new project folder under " \
                      "'data-store' on S3!"
                logger.exception(msg)
                raise Exception(msg)
    
    return file_name, uid


if __name__ == "__main__":
    main()
