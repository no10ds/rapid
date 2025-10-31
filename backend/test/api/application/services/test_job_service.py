from unittest.mock import patch

from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.application.services.job_service import JobService
from api.domain.Jobs.Job import JobStatus
from api.domain.Jobs.QueryJob import QueryStep, QueryJob
from api.domain.Jobs.UploadJob import UploadStep, UploadJob
from api.domain.dataset_metadata import DatasetMetadata


class TestGetAllJobs:
    def setup_method(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "get_jobs")
    def test_get_all_jobs(
        self,
        mock_get_jobs,
    ):
        expected = [
            {
                "type": "UPLOAD",
                "job_id": "abc-123",
                "status": "IN PROGRESS",
                "step": "VALIDATION",
                "errors": None,
                "filename": "filename1.csv",
            },
            {
                "type": "QUERY",
                "job_id": "def-456",
                "status": "FAILED",
                "step": "QUERY",
                "errors": ["Invalid column name"],
                "layer": "layer",
                "domain": "domain1",
                "dataset": "domain2",
                "result_url": None,
            },
        ]

        mock_get_jobs.return_value = expected

        result = self.job_service.get_all_jobs("111222333")

        assert result == expected
        mock_get_jobs.assert_called_once_with("111222333")


class TestGetJob:
    def setup_method(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "get_job")
    def test_get_single_job(self, mock_get_job):
        # GIVEN
        expected = {
            "type": "UPLOAD",
            "job_id": "abc-123",
            "status": "IN PROGRESS",
            "step": "VALIDATION",
            "errors": None,
            "filename": "filename1.csv",
        }

        mock_get_job.return_value = expected

        # WHEN
        result = self.job_service.get_job("abc-123")

        # THEN
        assert result == expected
        mock_get_job.assert_called_once_with("abc-123")


class TestCreateUploadJob:
    def setup_method(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "store_upload_job")
    def test_creates_upload_job(self, mock_store_upload_job):
        # GIVEN
        job_id = "abc-123"
        subject_id = "subject-123"
        filename = "file1.csv"
        raw_file_identifier = "123-456-789"
        domain = "domain1"
        dataset = "dataset1"
        version = 3
        layer = "layer"

        # WHEN
        result = self.job_service.create_upload_job(
            subject_id,
            job_id,
            filename,
            raw_file_identifier,
            DatasetMetadata(layer, domain, dataset, version),
        )

        # THEN
        assert result.job_id == job_id
        assert result.subject_id == subject_id
        assert result.filename == filename
        assert result.step == UploadStep.VALIDATION
        assert result.status == JobStatus.IN_PROGRESS
        mock_store_upload_job.assert_called_once_with(result)


class TestCreateQueryJob:
    def setup_method(self):
        self.job_service = JobService()

    @patch("api.domain.Jobs.Job.uuid")
    @patch.object(DynamoDBAdapter, "store_query_job")
    def test_creates_query_job(self, mock_store_query_job, mock_uuid):
        # GIVEN
        mock_uuid.uuid4.return_value = "abc-123"
        subject_id = "subject-123"
        domain = "test_domain"
        dataset = "test_dataset"
        version = 43
        layer = "layer"

        # WHEN
        result = self.job_service.create_query_job(
            subject_id, DatasetMetadata(layer, domain, dataset, version)
        )

        # THEN
        assert result.job_id == "abc-123"
        assert result.subject_id == subject_id
        assert result.step == QueryStep.INITIALISATION
        assert result.status == JobStatus.IN_PROGRESS
        mock_store_query_job.assert_called_once_with(result)


class TestUpdateJob:
    def setup_method(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "update_job")
    def test_updates_job(self, mock_update_job):
        # GIVEN
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            DatasetMetadata("layer", "domain1", "dataset2", 4),
        )

        assert job.step == UploadStep.VALIDATION

        # WHEN
        self.job_service.update_step(job, UploadStep.CLEAN_UP)

        # THEN
        assert job.step == UploadStep.CLEAN_UP
        mock_update_job.assert_called_once_with(job)

    @patch("api.domain.Jobs.Job.uuid")
    @patch.object(DynamoDBAdapter, "update_query_job")
    def test_sets_results_url_on_query_job(self, mock_update_query_job, mock_uuid):
        # GIVEN
        mock_uuid.uuid4.return_value = "abc-123"
        job = QueryJob(
            "subject-123", DatasetMetadata("layer", "domain1", "dataset2", 4)
        )

        assert job.results_url is None

        # WHEN
        self.job_service.set_results_url(job, "https://hello-there.com")

        # THEN
        assert job.results_url == "https://hello-there.com"
        mock_update_query_job.assert_called_once_with(job)


class TestSucceedsJob:
    def setup_method(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "update_job")
    def test_updates_job(self, mock_update_job):
        # GIVEN
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            DatasetMetadata("layer", "domain1", "dataset2", 4),
        )

        assert job.status == JobStatus.IN_PROGRESS

        # WHEN
        self.job_service.succeed(job)

        # THEN
        assert job.status == JobStatus.SUCCESS
        mock_update_job.assert_called_once_with(job)


class TestSucceedsQueryJob:
    def setup_method(self):
        self.job_service = JobService()

    @patch("api.domain.Jobs.Job.uuid")
    @patch.object(DynamoDBAdapter, "update_query_job")
    def test_succeeds_query_job(self, mock_update_query_job, mock_uuid):
        # GIVEN
        mock_uuid.uuid4.return_value = "abc-123"
        job = QueryJob(
            "subject-123", DatasetMetadata("layer", "domain1", "dataset2", 4)
        )
        url = "https://some-url.com"

        assert job.step == QueryStep.INITIALISATION
        assert job.status == JobStatus.IN_PROGRESS

        # WHEN
        self.job_service.succeed_query(job, url)

        # THEN
        assert job.step == QueryStep.NONE
        assert job.status == JobStatus.SUCCESS
        assert job.results_url == url
        mock_update_query_job.assert_called_once_with(job)


class TestFailsJob:
    def setup_method(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "update_job")
    def test_updates_job(self, mock_update_job):
        # GIVEN
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            DatasetMetadata("layer", "domain1", "dataset2", 4),
        )

        assert job.status == JobStatus.IN_PROGRESS

        # WHEN
        self.job_service.fail(job, ["error1", "error2"])

        # THEN
        assert job.status == JobStatus.FAILED
        assert job.errors == {"error1", "error2"}
        mock_update_job.assert_called_once_with(job)
