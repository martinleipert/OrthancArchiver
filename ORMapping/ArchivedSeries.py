from sqlalchemy import Column, Integer, String
from Base import Base


class ArchivedSeries(Base):
    __tablename__ = 'archived_series'

    # Identifiers
    _orthanc_series_id = Column(String, primary_key=True)
    _orthanc_study_id = Column(String)
    _orthanc_patient_id = Column(String)

    # ArchivingSpecificData
    _archiving_date = Column(String)
    _archive_location = Column(String)

    def __init__(self, orthanc_series_id, orthanc_study_id, orthanc_patient_id, archiving_date, archive_location):
        self._orthanc_series_id = orthanc_series_id
        self._orthanc_study_id = orthanc_study_id
        self._orthanc_patient_id = orthanc_patient_id

        self._archiving_date = archiving_date
        self._archive_location = archive_location
