from typing import Dict, List

from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.application.services.authorisation.authorisation_service import (
    match_permissions,
)
from api.common.config.auth import Action
from api.common.custom_exceptions import AuthorisationError
from api.common.logger import AppLogger
from api.domain.Jobs.Job import JobStep, Job, JobStatus, JobType
from api.domain.Jobs.QueryJob import QueryJob, QueryStep
from api.domain.Jobs.UploadJob import UploadJob


class JobService:
    def __init__(self, db_adapter=DynamoDBAdapter()):
        self.db_adapter = db_adapter

    def get_all_jobs(self, subject_id: str) -> list[Dict]:
        subject_permissions = self.db_adapter.get_permissions_for_subject(subject_id)
        all_jobs = self.db_adapter.get_jobs(subject_id)
        return self.filter_permitted_jobs(subject_permissions, all_jobs)

    def filter_permitted_jobs(
        self, permissions: List[str], jobs: List[Dict]
    ) -> List[Dict]:
        # Data admin can always see all jobs
        if Action.DATA_ADMIN.value in permissions:
            return jobs

        permitted_jobs = []

        for job in jobs:
            if job.get("type", None) == JobType.UPLOAD.value:
                # Can always see upload jobs
                permitted_jobs.append(job)
            if job.get("type", None) == JobType.QUERY.value:
                # Filter query jobs by what user is allowed to access
                domain = job.get("domain", None)
                dataset = job.get("dataset", None)
                if domain and dataset:
                    try:
                        match_permissions(
                            permissions,
                            [Action.READ.value],
                            domain,
                            dataset,
                        )
                        permitted_jobs.append(job)
                    except AuthorisationError:
                        pass
        return permitted_jobs

    def get_job(self, job_id: str) -> Dict:
        return self.db_adapter.get_job(job_id)

    def create_upload_job(
        self,
        subject_id: str,
        job_id: str,
        filename: str,
        raw_file_identifier: str,
        domain: str,
        dataset: str,
        version: int,
    ) -> UploadJob:
        job = UploadJob(
            subject_id, job_id, filename, raw_file_identifier, domain, dataset, version
        )
        self.db_adapter.store_upload_job(job)
        return job

    def create_query_job(
        self, subject_id: str, domain: str, dataset: str, version: int
    ) -> QueryJob:
        job = QueryJob(subject_id, domain, dataset, version)
        self.db_adapter.store_query_job(job)
        return job

    def update_step(self, job: Job, step: JobStep) -> None:
        AppLogger.info(f"Setting step for job {job.job_id} to {step.value}")
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
