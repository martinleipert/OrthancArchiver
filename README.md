
# Orthanc Archiver

Created for the Center of Computation of the University of La Serena \
by Martin Leipert \
martin.leipert@fau.de

## Summary 
Script that archives Dicom Files after a certain span of time from Orthanc.
This uses Orthanc's REST api to find out if a Dicom file is stored for longer then a certain time span.
The script checks the date on which the files were added.

If a Dicom file is outdated it is downloaded stored to a directory and a database entry is created with the information about the stored file. 
The database entries are managed in Python by the Object Relational Mapper SQLAlchemy. 

## Configuration
The behaviour of the script may be set by modifying the config.json.

Options implemented include:
* **OrthancURL**: IP adress and port (socket) of the Orthanc instance to access for archiving as a string.
* **PersistenceTimespan**: The timespan in days that has to elapse until a file gets archived.
* **ArchivePath**: Directory were the Dicom Series files will get Archived
* **DatabaseBackend**: The name of the backend to use (until now only SQLite is implemented)

Specific Backends:
* **SQLite** for a simple database stored in a file \
        Options \
      * **FilePath**: Filename of the SQLite database