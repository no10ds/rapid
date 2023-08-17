from typing import Dict, List

from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.common.logger import AppLogger
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.Jobs.Job import JobStep, Job, JobStatus
from api.domain.Jobs.QueryJob import QueryJob, QueryStep
from api.domain.Jobs.UploadJob import UploadJob


class JobService:
    def __init__(self, db_adapter=DynamoDBAdapter()):
        self.db_adapter = db_adapter

    def get_all_jobs(self, subject_id: str) -> list[Dict]:
        return self.db_adapter.get_jobs(subject_id)

    def get_job(self, job_id: str) -> Dict:
        return self.db_adapter.get_job(job_id)

    def create_upload_job(
        self,
        subject_id: str,
        job_id: str,
        filename: str,
        raw_file_identifier: str,
        dataset: DatasetMetadata,
    ) -> UploadJob:
        job = UploadJob(subject_id, job_id, filename, raw_file_identifier, dataset)
        self.db_adapter.store_upload_job(job)
        return job

    def create_query_job(self, subject_id: str, dataset: DatasetMetadata) -> QueryJob:
        job = QueryJob(subject_id, dataset)
        self.db_adapter.store_query_job(job)
        return job

    def update_step(self, job: Job, step: JobStep) -> None:
        AppLogger.info(f"Setting step for job {job.job_id} to {step}")
        job.set_step(step)
        self.db_adapter.update_job(job)

    def succeed(self, job: Job) -> None:
        AppLogger.info(f"Job {job.job_id} has succeeded")
        job.set_status(JobStatus.SUCCESS)
        self.db_adapter.update_job(job)

    def fail(self, job: Job, errors: List[str]) -> None:
        AppLogger.info(f"Job {job.job_id} has failed")
        job.set_status(JobStatus.FAILED)
        job.set_errors(set(errors))
        self.db_adapter.update_job(job)

    def succeed_query(self, query_job: QueryJob, url: str) -> None:
        AppLogger.info(f"Query job {query_job.job_id} has succeeded")
        query_job.set_step(QueryStep.NONE)
        query_job.set_results_url(url)
        query_job.set_status(JobStatus.SUCCESS)
        self.db_adapter.update_query_job(query_job)

    def set_results_url(self, query_job: QueryJob, url: str) -> None:
        AppLogger.info(f"Setting query results URL on {query_job.job_id}")
        query_job.set_results_url(url)
        self.db_adapter.update_query_job(query_job)
