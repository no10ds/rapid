import time
from typing import Optional

from api.common.config.constants import QUERY_JOB_EXPIRY_DAYS
from api.common.config.layers import Layer
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.Jobs.Job import Job, JobType, JobStep


class QueryStep(JobStep):
    INITIALISATION = "INITIALISATION"
    RUNNING = "RUNNING"
    GENERATING_RESULTS = "GENERATING_RESULTS"
    NONE = "-"


class QueryJob(Job):
    def __init__(self, subject_id: str, dataset: DatasetMetadata):
        super().__init__(JobType.QUERY, QueryStep.INITIALISATION, subject_id)
        self.layer: Layer = dataset.layer
        self.domain: str = dataset.domain
        self.dataset: str = dataset.dataset
        self.version: int = dataset.version
        self.results_url: Optional[str] = None
        self.expiry_time: int = int(time.time() + QUERY_JOB_EXPIRY_DAYS * 24 * 60 * 60)

    def set_results_url(self, url: str) -> None:
        self.results_url = url
