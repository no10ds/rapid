import time

from api.common.config.constants import UPLOAD_JOB_EXPIRY_DAYS
from api.common.config.layers import Layer
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.Jobs.Job import Job, JobType, JobStep


class UploadStep(JobStep):
    VALIDATION = "VALIDATION"
    RAW_DATA_UPLOAD = "RAW_DATA_UPLOAD"
    DATA_UPLOAD = "DATA_UPLOAD"
    LOAD_PARTITIONS = "LOAD_PARTITIONS"
    CLEAN_UP = "CLEAN_UP"
    NONE = "-"


class UploadJob(Job):
    def __init__(
        self,
        subject_id: str,
        job_id: str,
        filename: str,
        raw_file_identifier: str,
        dataset: DatasetMetadata,
    ):
        super().__init__(JobType.UPLOAD, UploadStep.VALIDATION, subject_id, job_id)
        self.filename: str = filename
        self.raw_file_identifier: str = raw_file_identifier
        self.layer: Layer = dataset.layer
        self.domain: str = dataset.domain
        self.dataset: str = dataset.dataset
        self.version: int = dataset.version
        self.expiry_time: int = int(time.time() + UPLOAD_JOB_EXPIRY_DAYS * 24 * 60 * 60)
