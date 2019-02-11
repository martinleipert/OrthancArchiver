"""
By Martin Leipert
martin.leipert@fau.de
Initially created at 11.09.2018
for the Center of Computation of the universidad de La Serena in La Serena, Chile

Example script for archiving files from Orthanc after a certain period
Scans Orthanc for files which are stored for longer than a certain period and downloads them using the
REST Api of Orthanc

VERSIONS:

v0.1 as of 13.09.2018:
    * Implemented basic functionality:
        - Argparsing and configuration
        - Get outdated series
        - Archiving of series in tarballs
        - Remove them from server
        - Store in a database with basic data
    * Only archives Series and stores base tags
    * Only SQLite backend

v0.2
    @TODO more database backends like MySQL
    @TODO more complete archiving with more metadata and cross references in ORM
    @TODO integrate to shellscript
    @TODO full testing environment
    @TODO Custom metadata archived instances in database of Orthanc
"""

# Package to parse json headers
import json
# Parse arguments from command line
import argparse
# SQL Alchemy -> Object Relational Mapping to store the record
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Self-written storage objects
from ORMapping.Base import Base
from ORMapping.ArchivedInstances import ArchivedInstance
from ORMapping.ArchivedSeries import ArchivedSeries
# Handle urls and HTTP requests
import urllib2
# Time and Date utility
import datetime
# File and Path Handling
import shutil
import os
# For compression for storage on streamers
import tarfile

# Some constants
TIME_FORMAT = "%Y%m%dT%H%M%S"


"""
Main method
    1. Parse the configuration
    2. Start database connection
    3. Check files on the orthanc server
    4. If files are older then configured -> archive files and remove from server
    5. Store the archiving records in the database
"""


def main():
    # Argument parser containing all required and optional arguments
    parser = argparse.ArgumentParser()
    # A json configuration file which is used to setup the script
    # Mainly contains important parameters relevant for archiving and indexing
    parser.add_argument("-cF", "--configurationFile", default="./config.json",
                        help="*.json file containing the configuration of the dicom archiving")
    args = parser.parse_args()

    # region Configuration reading
    # Open the configuration and read
    open_file = open(args.configurationFile, "r")

    # Get the full content of the file
    json_full_text = open_file.read()

    # Close the file again
    open_file.close()

    # Parse the json configuration which contains:
    parsed_json = json.loads(json_full_text)


    # @TODO method for checking the keys and extract them each single key -> State error if thats not the case
    # The Orthanc server-url to take the backups from
    # Orthanc Server URL with port: "OrthancURL" = "127.0.0.1:8042"
    server_url = parsed_json["OrthancURL"]

    # The timespan a dataset stays in the PACS after the last update in days (integer)
    # PersistenceTimespan: "PersistenceTimespan" = 180
    persistent_timespan = parsed_json["PersistenceTimespan"]

    # The path to the Archive as absolute path
    # ArchivePath: "ArchivePath" = "/sda3/archive/"
    archive_path = parsed_json["ArchivePath"]

    # Select the database backend
    database_backend = parsed_json["DatabaseBackend"]
    # endregion

    #region Setup and start
    # the configuration of the used database
    # for the object relational mapper

    # Reserve the engine variable for sqlAlchemy
    # As the engines may be exchanged by backend
    engine = None

    # If the backend is SQLite connect to database file (if database not yet exists
    if database_backend == "SQLite":
        sqlite_settings = parsed_json[database_backend]
        file_path = sqlite_settings['FilePath']

        # Start SQLite connection to local file
        engine_path = "sqlite:///%s" % file_path
        engine = create_engine(engine_path)

    # If the backend is MySQL
    elif database_backend == "MySQL":
        # @TODO implement MySQL connection
        pass

    # @TODO prepare other backends
    else:
        Exception("Unknown database engine %s" % database_backend)

    # Bind the data
    Base.metadata.create_all(engine)

    # Start database session -> Create a class
    DatabaseSession = sessionmaker(bind=engine)

    # Call constructor to start session
    database_session = DatabaseSession()
    #endregion

    #region Prepare download
    # Get the timedelta and the current time to check if archiving the series is required
    persistence_time_difference = datetime.timedelta(days=persistent_timespan)
    current_time = datetime.datetime.now()

    # Prepare the archive folder
    current_date_str = current_time.strftime("%Y%m%d")
    todays_archive_path = os.path.join(archive_path, current_date_str)
    if not os.path.exists(todays_archive_path):
        os.mkdir(todays_archive_path)

    # Get the listed series via http request
    series_list_url = r"http://%s/series" % server_url
    request = urllib2.urlopen(series_list_url)
    series_list_str = request.fp.read()

    # Parse the corresponding series from json to a list
    series_list = json.loads(series_list_str)
    #endregion Prepare download

    # region Iterate over Filelist
    # Iterate over saved series
    # @TODO more intelligent queries - e.g. query only those who are older than a certain amount of time
    for series_id in series_list:

        # Store the files in a list to clean up the instances after archiving
        instances_for_cleanup = []

        # Request the series json information
        single_series_url = "%s/%s" % (series_list_url, series_id)
        request = urllib2.urlopen(single_series_url)
        series_json_text = request.fp.read()
        single_series_json = json.loads(series_json_text)

        # Extract the time the series was updated last
        last_update_str = single_series_json['LastUpdate']
        last_update = datetime.datetime.strptime(last_update_str, TIME_FORMAT)

        # Check the time diffeence
        time_difference_last_update = current_time - last_update

        # Check if the file should be kept
        if time_difference_last_update > persistence_time_difference:
            # If it should not be kept -> Archive the series
            series_instances = single_series_json["Instances"]

            # Extract further metadata for the Study and the patient
            study_id = single_series_json["ParentStudy"]

            # Get the study metadata as json
            single_study_url = "http://%s/studies/%s/" % (server_url, study_id)
            request = urllib2.urlopen(single_study_url)
            single_study_text = request.fp.read()
            single_study_json = json.loads(single_study_text)

            # Get the data of the parent study
            patient_id = single_study_json["ParentPatient"]

            # Pack series to archive to a tar file
            series_archive_path = "%s.tar" % series_id

            # Add the series to a tgz file for storage on magnetic band
            with tarfile.open(series_archive_path, "w:gz") as open_tar_file:

                # Add all instances of the series to the tar
                for single_instance_id in series_instances:

                    # Downloadpath -> Get via REST API
                    single_instance_download_url = "http://%s/instances/%s/file" % (server_url, single_instance_id)

                    # Open the url
                    request = urllib2.urlopen(single_instance_download_url)

                    # Generate a file name
                    instance_file_path = "%s.dcm" % single_instance_id

                    # Open the file and write the url content
                    with open(instance_file_path, "w") as instance_file:
                        instance_file.write(request.fp.read())

                    # Add the instance to the tar
                    open_tar_file.add(instance_file_path)

                    # Add the temporary files to the cleanup after the packing
                    instances_for_cleanup.add(instance_file_path)

            # Generate the path to the archive
            archived_series_location = os.path.join(todays_archive_path, series_archive_path)

            # Move the archived series to archive directory
            shutil.move(series_archive_path, archived_series_location)

            # Store information about the archived series in the
            archived_series = ArchivedSeries(series_id, study_id, patient_id, current_date_str,
                                             archived_series_location)
            database_session.add(archived_series)

            # TODO test
            # Delete resource on the server
            urllib2.urlopen(single_series_url, method='DELETE')

            # @TODO check if patient and study need to be archived

            # Remove temporarily stored instances
            for instance_to_clean_up in instances_for_cleanup:
                os.remove(instance_to_clean_up)

    # endregion
    # region closing

    # Commit the added archives to the archive db
    database_session.commit()
    database_session.close()

    # endregion closing

if __name__ == "__main__":
    main()
