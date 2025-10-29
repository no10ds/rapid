from strenum import StrEnum
import time
from typing import Optional, Set
import uuid

from api.common.config.constants import DEFAULT_JOB_EXPIRY_DAYS


class JobStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    IN_PROGRESS = "IN PROGRESS"


class JobType(StrEnum):
    QUERY = "QUERY"
    UPLOAD = "UPLOAD"


class JobStep(StrEnum):
    pass


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Job:
    def __init__(
        self,
        job_type: JobType,
        step: JobStep,
        subject_id: str,
        job_id: Optional[str] = None,
    ):
        self.step: JobStep = step
        self.job_type: JobType = job_type
        self.subject_id: str = subject_id
        self.status: JobStatus = JobStatus.IN_PROGRESS
        self.job_id: str = job_id if job_id else generate_uuid()
        self.errors: Set[str] = set()
        self.expiry_time: int = int(
            time.time() + DEFAULT_JOB_EXPIRY_DAYS * 24 * 60 * 60
        )

    def set_step(self, step: JobStep) -> None:
        self.step = step

    def set_status(self, status: JobStatus):
        self.status = status

    def set_errors(self, errors: Set[str]):
        self.errors = errors
