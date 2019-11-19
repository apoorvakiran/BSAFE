#!/anaconda3/bin//python
"""
This script is used to interact with Iterate Lab Inc.'s Data Store.
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

import hashlib
from getpass import getuser
import datetime
import logging
import argparse
import uuid
import ipinfo
from constants import valid_teams
import botocore
from database import BackendDataBase
from ergo_analytics import upload_data_to_aws_s3
from ergo_analytics import download_from_aws_s3


logger = logging.getLogger()

DATA_STORE_S3_BUCKET = "data-store-iterate-labs"


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
    parser.add_argument('--upload', nargs=2, metavar=('<data file>',
                                                      '<project ID>'),
                        help='Upload a single file to the project ID in'
                             'the Data Store')
    # User can upload data to a bucket
    parser.add_argument('--list-available-projects',
                        action='store_true',
                        help='List all available projects in the Data Store. '
                             'This can help retrieve project IDs and '
                             'project names.')
    parser.add_argument('--project-id', nargs=1, metavar='<project ID>',
                        help='Upload data to the Data Store for'
                             'this project ID.')
    parser.add_argument('--data-type', nargs=1, metavar='<dev/test/prod>',
                        help='What type of data is this? Is it development'
                             'of the code, one-off testing or collected in'
                             'production? Plays the role of a tag but is more'
                             'formal', default='unlabeled')
    parser.add_argument('--project-details', nargs=1, metavar='<project ID>',
                        help='Returns details for a project given its ID.')
    parser.add_argument('--list-all-files', nargs=1, metavar='<project ID>',
                        help='Lists all files uploaded for a given'
                             'project given its ID.')
    parser.add_argument('--download-all-files', nargs=2,
                        metavar=('<project ID>', '<download to local folder>'),
                        help='Downloads all files uploaded for a given'
                             'project given its ID to a local folder.')
    parser.add_argument('--tags', nargs="+", metavar='<tag>',
                        help='Associate a set of tags with a data file '
                             'being uploaded. The tag goes in the '
                             'meta-data database. For example (2 tags added): '
                             '--tags "this is tag1" "this is tag 2"')

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
                  "Call this script again with --help to see email\n" \
                  "contact for valid options."
            logger.exception(msg)
            raise Exception(msg)

        project = \
           project.replace(" ", "-").replace("_", "-").rstrip().lstrip().lower()

        if len(team) == 0 or len(project) == 0:
            msg = "Please provide valid team and/or project!"
            raise Exception(msg)

        create_project_in_database(db=db, team=team, project_name=project)

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

    elif args.upload is not None and len(args.upload) == 2:
        """
        Upload data to the Data Store. Note that Project ID needs to be
        given as well in this case.
        """
        msg = "Upload data to existing project!"
        logger.debug(msg)

        project_id = args.upload[1]
        if not project_exists(db=db, project_id=project_id):
            msg = f"Project with ID '{project_id}' does not exist!"
            logger.exception(msg)
            raise Exception(msg)

        # so here is the process: The data gets assigned a unique data ID
        # then it gets uploaded to S3.
        # We then also store in the Meta-Data table information about the
        # data ID and associted project ID including the link to S3 etc.
        # This was the database contains all information on what has ever
        # been uploaded by us and the data happily lives in S3:

        data_file_to_upload = args.upload[0]

        if not os.path.isfile(data_file_to_upload):
            msg = f"Data file '{data_file_to_upload}' not found!"
            logger.exception(msg)
            raise Exception(msg)

        s3_url, s3_name, uid = upload_data(db=db,
                                           file_to_upload=data_file_to_upload,
                                           project_id=project_id)

        additional_tags = [] if not (args.tags is not None and
                                     len(args.tags) > 0) else args.tags

        # get the kind of data as well (the type if you will). Suggestions:
        # Was it collected during code development (dev), during testing
        # (test), or during production (prod) -- or any other tag you
        # want to use:
        data_type = args.data_type[0]

        # now we put this information - with more - in the database
        # (the meta-data that is):
        register_data_in_database(db=db, s3_url=s3_url,
                                  additional_tags=additional_tags,
                                  s3_name=s3_name, uid=uid,
                                  project_id=project_id,
                                  data_type=data_type,
                                  file_to_upload=data_file_to_upload)

        msg = f"\nFile '{data_file_to_upload}' successfully uploaded to " \
              f"project '{project_id}'.\n"
        logger.info(msg)
        print(msg)

    elif args.project_details is not None and len(args.project_details) == 1:

        project_id = args.project_details[0]

        if not project_exists(db=db, project_id=project_id):
            msg = f"Project with ID '{project_id}' does not exist!"
            logger.exception(msg)
            raise Exception(msg)

        project_details = db.get_project_details(project_id=project_id)

        msg = f"Print project details for ID: '{project_id}'."
        logger.info(msg)
        print(msg)
        for k, v in project_details.items():
            print(f"  - '{k}' = '{v}'")
        print()

    elif args.list_all_files:

        project_id = args.list_all_files[0]

        if not project_exists(db=db, project_id=project_id):
            msg = f"Project with ID '{project_id}' does not exist!"
            logger.exception(msg)
            raise Exception(msg)

        files = db.list_all_files_for_project(project_id=project_id)

        msg = f"Found {len(files)} files associated with " \
              f"project ID = {project_id}"
        logger.info(msg)

        print(f"Listing all files for project ID: {project_id}...")
        for fix, file in enumerate(files):
            print(f" ({fix + 1}) - ID: '{file['Data_ID']}' at "
                  f"S3 path '{file['s3_name']}'")

        msg = "Successfully listed all files."
        logger.info(msg)

    elif args.download_all_files:

        project_id = args.download_all_files[0]

        if not project_exists(db=db, project_id=project_id):
            msg = f"Project with ID '{project_id}' does not exist!"
            logger.exception(msg)
            raise Exception(msg)

        files = db.list_all_files_for_project(project_id=project_id)

        msg = f"Found {len(files)} files associated with " \
              f"project ID = {project_id}"
        print(msg)
        logger.info(msg)

        if len(files) == 0:
            msg = "No files found for this project!"
            print(msg)
            logger.info(msg)
            return

        local_folder = args.download_all_files[1]

        if os.path.isdir(local_folder):
                msg = f"The local folder '{local_folder}' already exists!"
                logger.exception(msg)
                print(msg)
                raise Exception(msg)

        os.mkdir(local_folder)

        msg = f"Downloading all files for " \
              f"project ID: {project_id} to local folder: {local_folder}..."
        logger.info(msg)
        print(msg)
        for fix, file in enumerate(files):

            local_name = os.path.join(local_folder, file['s3_name'].split('/')[-1])

            download_from_aws_s3(bucketname='data-store-iterate-labs',
                                 s3_name=file['s3_name'],
                                 local_filename=local_name)

            print(f" ({fix + 1}) - Download complete: "
                  f"ID: '{file['Data_ID']}' from S3 path '{file['s3_name']}'")

        msg = f"Successfully downloaded all files to '{local_folder}'."
        print(msg)
        logger.info(msg)

    else:
        parser.print_help()
        return

    msg = "Done."
    print(msg)
    logger.debug(msg)


def project_exists(db=None, project_id=None):
    """
    Does the incoming project ID exist in the Data Store?
    """
    return db.check_that_project_exists(project_id=project_id)


def check_response(response=None):
    """
    Checks the response status when interacting with SDB.
    Raises and exception if there was an error in the response.
    """
    if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
        msg = "Error in connecting to the SDB!"
        logger.exception(msg)
        raise Exception(msg)


def hash_a_file(file=None):
    """
    Takes in a file and hashes it. This is useful to quickly check if
    two files are identical.
    """

    BUF_SIZE = 2 * 65536  # lets read stuff in 128kb chunks!

    sha1 = hashlib.sha1()

    with open(file, 'rb') as f:
        while True:

            data = f.read(BUF_SIZE)

            if not data:
                # no more data
                break

            sha1.update(data)

    return sha1.hexdigest()


def register_data_in_database(db=None, s3_url=None, s3_name=None, uid=None,
                              project_id=None, file_to_upload=None,
                              additional_tags=None, data_type=None):
    """
    Registers meta-data related to a datum in the Data Store backend database.
    The datum is stored on S3.
    """
    project_details = db.get_project_details(project_id=project_id)

    data_id = s3_name

    # create a hash of the file content:
    file_hash = hash_a_file(file=file_to_upload)

    response = db.register_data_in_database(
        additional_tags=additional_tags,
        data_id=data_id, file_hash=file_hash,
        s3_url=s3_url, s3_name=s3_name,
                                uid=uid, project_id=project_id,
                                project_name=project_details['Project_Name'],
                                team_name=project_details['Team_Name'],
                                data_type=data_type,
                                **get_common_tags()
                                )

    if not response:
        msg = "There was an error registering the data in the database!"
        logger.exception(msg)
        raise Exception(msg)


def get_project_id(team=None, project=None):
    """
    Construct the project ID and returns it - this is the key to be used in
    the data store.
    """
    proposed_project_id = team + '-' + project  # unique to this project

    return proposed_project_id


def get_common_tags():
    """
    Put together some common tags (like user, IP, etc.) across all database
    tables.
    """
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

    common = dict(ip_info_token=ip_info_token,
                  created_by_user=user_name,
                  time_created_utc=str(datetime.datetime.utcnow()),
                  ip=geo_tag['ip'],
                  hostname=geo_tag['hostname'],
                  country=geo_tag['country'],
                  location=geo_tag['loc'],
                  timezone=geo_tag['timezone'],
                  created_by_system_user_name=getuser(),
                  aws_access_key=aws_access_key
                  )

    return common


def create_project_in_database(db=None, team=None, project_name=None):
    """
    Creates a new project in the data store. This project is associated
    with a set of data.

    Returns the bucket_name of the successfully created bucket and
    the randomly generated ID associated with it.
    """
    project_id = get_project_id(team=team, project=project_name)

    db.insert_project_if_not_exist(project_id=project_id,
                                   team_name=team, project_name=project_name,
                                   **get_common_tags()
                                   )

    msg = f"\nProject ID '{project_id}' created in the Data Store!\n" \
          f"Now you can upload data to this project.\n"
    print(msg)
    logger.debug(msg)


def generate_unique_id():
    """
    Generates a unique ID - used to generate valid S3 file names.
    """
    return str(uuid.uuid4())


def upload_data(db=None, file_to_upload=None, project_id=None):
    """
    Uploads the "file_to_upload" to the project associated with
    the ID "project_id".
    """

    # first, get project name and team name from the project id:
    project_details = db.get_project_details(project_id=project_id)

    project_name = project_details['Project_Name']
    team_name = project_details['Team_Name']

    max_tries = 10
    n = 0
    while True:
        # keep re-creating unique ID's until good:
        uid = generate_unique_id()  # try another random ID until we succeed
        s3_name = f"{team_name}/{project_name}/data-{uid}"
        try:
            logger.debug(f"Trying s3 file name = {s3_name}")

            upload_data_to_aws_s3(bucketname=DATA_STORE_S3_BUCKET,
                                  name_on_s3=s3_name,
                                  local_filename=file_to_upload)
            break  # we got a valid name
        except botocore.exceptions.ClientError:
            msg = f"Please enter a valid s3 bucket name " \
                  f"'{s3_name}'!\nCheck the team and project names!"
            logger.exception(msg)
            raise Exception(msg)
        except Exception:
            n += 1
            if n > max_tries:
                msg = "Was unable to create a new project folder under\n" \
                      "'data-store-iterate-labs' on the company's S3!"
                logger.exception(msg)
                raise Exception(msg)

    s3_url = f"https://{DATA_STORE_S3_BUCKET}.s3.amazonaws.com/{s3_name}"

    return s3_url, s3_name, uid


if __name__ == "__main__":
    """
    Run this as a script
    """
    main()
