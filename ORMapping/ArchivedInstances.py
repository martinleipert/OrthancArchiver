from sqlalchemy import Column, Integer, String
from Base import Base

"""
Martin Leipert
martin.leipert@fau.de

Store a Dicom Instance from Orthanc in an archive database
with the Object Realtional Mapper SQLAlchemy

-> Currently unused
"""

class ArchivedInstance(Base):
    __tablename__ = 'archived_instances'

    # Identifiers
    _orthanc_instance_id = Column(String, primary_key=True)
    _orthanc_series_id = Column(String)
    _orthanc_study_id = Column(String)
    _orthanc_patient_id = Column(String)

    # ArchivingSpecificData
    _archiving_date = Column(String)
    _archive_location = Column(String)

    def __init__(self, orthanc_instance_id, orthanc_series_id, orthanc_study_id, orthanc_patient_id, archiving_date,
                 archive_location):
        self._orthanc_instance_id = orthanc_instance_id
        self._orthanc_series_id = orthanc_series_id
        self._orthanc_study_id = orthanc_study_id
        self._orthanc_patient_id = orthanc_patient_id

        self._archiving_date = archiving_date
        self._archive_location = archive_location
