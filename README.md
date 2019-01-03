By Martin Leipert \
martin.leipert@fau.de

Created for the Center of Computation of the University of La Serena 

Script that archives Dicom Files after a certain span of time from Orthanc.
This uses Orthanc's REST api to find out if a Dicom file is stored for longer then a certain time span.
The script checks this automatically and repeatedly after a certain amount of time.

If a Dicom file is outdated it is downloaded stored to a directory and a database entry is created with the information about the stored file. 
The database entries are managed in Python by the Object Relational Mapper SQLAlchemy. 

The behaviour of the script may be set by modifying the config.json.

Options implemented include:
* OrthancURL : IP adress and port (socket) of the Orthanc instance to access for archiving.
* PersistenceTimespan : The timespan that has to elapse until a file gets archived.
* ArchivePath : Directory were the Dicom Files will get archived
* DatabaseBackend : The name of the backend to use (until now only SQLite is implemented)