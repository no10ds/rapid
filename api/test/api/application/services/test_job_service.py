from unittest.mock import patch

from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.adapter.s3_adapter import S3Adapter
from api.application.services.job_service import JobService
from api.application.services.protected_domain_service import ProtectedDomainService
from api.common.config.auth import SensitivityLevel
from api.domain.Jobs.Job import JobStatus
from api.domain.Jobs.QueryJob import QueryStep, QueryJob
from api.domain.Jobs.UploadJob import UploadStep, UploadJob


class TestGetAllJobs:
    def setup(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "get_jobs")
    @patch.object(S3Adapter, "get_dataset_sensitivity")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    @patch.object(ProtectedDomainService, "list_protected_domains")
    def test_get_all_jobs_when_permitted(
        self,
        mock_list_protected_domains,
        mock_get_permissions_for_subject,
        mock_get_dataset_sensitivity,
        mock_get_jobs,
    ):
        # GIVEN
        mock_get_permissions_for_subject.return_value = ["READ_ALL"]
        mock_get_dataset_sensitivity.return_value = SensitivityLevel.PUBLIC
        mock_list_protected_domains.return_value = {}

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
                "domain": "domain1",
                "dataset": "domain2",
                "result_url": None,
            },
        ]

        mock_get_jobs.return_value = expected

        # WHEN
        result = self.job_service.get_all_jobs("111222333")

        # THEN
        assert result == expected
        mock_get_jobs.assert_called_once()
        mock_get_permissions_for_subject.assert_called_once_with("111222333")

    @patch.object(DynamoDBAdapter, "get_jobs")
    @patch.object(S3Adapter, "get_dataset_sensitivity")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    @patch.object(ProtectedDomainService, "list_protected_domains")
    def test_get_only_upload_jobs_when_no_read_permissions(
        self,
        mock_list_protected_domains,
        mock_get_permissions_for_subject,
        mock_get_dataset_sensitivity,
        mock_get_jobs,
    ):
        # GIVEN
        mock_get_permissions_for_subject.return_value = ["WRITE_ALL"]
        mock_get_dataset_sensitivity.return_value = SensitivityLevel.PUBLIC
        mock_list_protected_domains.return_value = {}

        all_jobs = [
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
                "domain": "domain1",
                "dataset": "domain2",
                "result_url": None,
            },
        ]

        expected = [
            {
                "type": "UPLOAD",
                "job_id": "abc-123",
                "status": "IN PROGRESS",
                "step": "VALIDATION",
                "errors": None,
                "filename": "filename1.csv",
            }
        ]

        mock_get_jobs.return_value = all_jobs

        # WHEN
        result = self.job_service.get_all_jobs("111222333")

        # THEN
        assert result == expected
        mock_get_jobs.assert_called_once()
        mock_get_permissions_for_subject.assert_called_once_with("111222333")

    @patch.object(DynamoDBAdapter, "get_jobs")
    @patch.object(S3Adapter, "get_dataset_sensitivity")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    @patch.object(ProtectedDomainService, "list_protected_domains")
    def test_get_all_upload_and_allowed_protected_jobs_when_appropriate_permissions(
        self,
        mock_list_protected_domains,
        mock_get_permissions_for_subject,
        mock_get_dataset_sensitivity,
        mock_get_jobs,
    ):
        # GIVEN
        mock_get_permissions_for_subject.return_value = ["READ_PROTECTED_DOMAIN1"]
        mock_get_dataset_sensitivity.side_effect = [
            SensitivityLevel.PROTECTED,
            SensitivityLevel.PROTECTED,
            SensitivityLevel.PRIVATE,
        ]
        mock_list_protected_domains.return_value = {"domain1", "domain3"}

        all_jobs = [
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
                "domain": "domain1",
                "dataset": "dataset2",
                "result_url": None,
            },
            {
                "type": "QUERY",
                "job_id": "uvw-456",
                "status": "SUCCESS",
                "step": "QUERY",
                "errors": None,
                "domain": "domain2",
                "dataset": "dataset3",
                "result_url": "http://something.com",
            },
            {
                "type": "QUERY",
                "job_id": "xyz-456",
                "status": "FAILED",
                "step": "QUERY",
                "errors": ["Invalid column name"],
                "domain": "domain4",
                "dataset": "dataset9",
                "result_url": None,
            },
        ]

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
                "domain": "domain1",
                "dataset": "dataset2",
                "result_url": None,
            },
        ]

        mock_get_jobs.return_value = all_jobs

        # WHEN
        result = self.job_service.get_all_jobs("111222333")

        # THEN
        assert result == expected
        mock_get_jobs.assert_called_once()
        mock_get_permissions_for_subject.assert_called_once_with("111222333")

    @patch.object(DynamoDBAdapter, "get_jobs")
    @patch.object(S3Adapter, "get_dataset_sensitivity")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    @patch.object(ProtectedDomainService, "list_protected_domains")
    def test_get_all_upload_and_query_jobs_for_sensitive_dataset_when_appropriate_permissions(
        self,
        mock_list_protected_domains,
        mock_get_permissions_for_subject,
        mock_get_dataset_sensitivity,
        mock_get_jobs,
    ):
        # GIVEN
        mock_get_permissions_for_subject.return_value = ["READ_PRIVATE"]
        mock_get_dataset_sensitivity.side_effect = [
            SensitivityLevel.PROTECTED,
            SensitivityLevel.PRIVATE,
        ]
        mock_list_protected_domains.return_value = {"domain1"}

        all_jobs = [
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
                "domain": "domain1",
                "dataset": "dataset2",
                "result_url": None,
            },
            {
                "type": "QUERY",
                "job_id": "uvw-456",
                "status": "SUCCESS",
                "step": "QUERY",
                "errors": None,
                "domain": "domain2",
                "dataset": "dataset3",
                "result_url": "http://something.com",
            },
        ]

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
                "job_id": "uvw-456",
                "status": "SUCCESS",
                "step": "QUERY",
                "errors": None,
                "domain": "domain2",
                "dataset": "dataset3",
                "result_url": "http://something.com",
            },
        ]

        mock_get_jobs.return_value = all_jobs

        # WHEN
        result = self.job_service.get_all_jobs("111222333")

        # THEN
        assert result == expected
        mock_get_jobs.assert_called_once()
        mock_get_permissions_for_subject.assert_called_once_with("111222333")

    @patch.object(DynamoDBAdapter, "get_jobs")
    @patch.object(S3Adapter, "get_dataset_sensitivity")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    @patch.object(ProtectedDomainService, "list_protected_domains")
    def test_get_all_jobs_when_data_admin(
        self,
        mock_list_protected_domains,
        mock_get_permissions_for_subject,
        mock_get_dataset_sensitivity,
        mock_get_jobs,
    ):
        # GIVEN
        mock_get_permissions_for_subject.return_value = ["DATA_ADMIN"]
        mock_get_dataset_sensitivity.side_effect = [
            SensitivityLevel.PROTECTED,
            SensitivityLevel.PRIVATE,
        ]
        mock_list_protected_domains.return_value = {"domain1"}

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
                "domain": "domain1",
                "dataset": "dataset2",
                "result_url": None,
            },
            {
                "type": "QUERY",
                "job_id": "uvw-456",
                "status": "SUCCESS",
                "step": "QUERY",
                "errors": None,
                "domain": "domain2",
                "dataset": "dataset3",
                "result_url": "http://something.com",
            },
        ]

        mock_get_jobs.return_value = expected

        # WHEN
        result = self.job_service.get_all_jobs("111222333")

        # THEN
        assert result == expected
        mock_get_jobs.assert_called_once()
        mock_get_permissions_for_subject.assert_called_once_with("111222333")


class TestGetJob:
    def setup(self):
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
    def setup(self):
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

        # WHEN
        result = self.job_service.create_upload_job(
            subject_id, job_id, filename, raw_file_identifier, domain, dataset, version
        )

        # THEN
        assert result.job_id == job_id
        assert result.subject_id == subject_id
        assert result.filename == filename
        assert result.step == UploadStep.INITIALISATION
        assert result.status == JobStatus.IN_PROGRESS
        mock_store_upload_job.assert_called_once_with(result)


class TestCreateQueryJob:
    def setup(self):
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

        # WHEN
        result = self.job_service.create_query_job(subject_id, domain, dataset, version)

        # THEN
        assert result.job_id == "abc-123"
        assert result.subject_id == subject_id
        assert result.step == QueryStep.INITIALISATION
        assert result.status == JobStatus.IN_PROGRESS
        mock_store_query_job.assert_called_once_with(result)


class TestUpdateJob:
    def setup(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "update_job")
    def test_updates_job(self, mock_update_job):
        # GIVEN
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            "domain1",
            "dataset2",
            4,
        )

        assert job.step == UploadStep.INITIALISATION

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
        job = QueryJob("subject-123", "domain1", "dataset2", 4)

        assert job.results_url is None

        # WHEN
        self.job_service.set_results_url(job, "https://hello-there.com")

        # THEN
        assert job.results_url == "https://hello-there.com"
        mock_update_query_job.assert_called_once_with(job)


class TestSucceedsJob:
    def setup(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "update_job")
    def test_updates_job(self, mock_update_job):
        # GIVEN
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            "domain1",
            "dataset2",
            4,
        )

        assert job.status == JobStatus.IN_PROGRESS

        # WHEN
        self.job_service.succeed(job)

        # THEN
        assert job.status == JobStatus.SUCCESS
        mock_update_job.assert_called_once_with(job)


class TestSucceedsQueryJob:
    def setup(self):
        self.job_service = JobService()

    @patch("api.domain.Jobs.Job.uuid")
    @patch.object(DynamoDBAdapter, "update_query_job")
    def test_succeeds_query_job(self, mock_update_query_job, mock_uuid):
        # GIVEN
        mock_uuid.uuid4.return_value = "abc-123"
        job = QueryJob("subject-123", "domain1", "dataset2", 4)
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
    def setup(self):
        self.job_service = JobService()

    @patch.object(DynamoDBAdapter, "update_job")
    def test_updates_job(self, mock_update_job):
        # GIVEN
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            "domain1",
            "dataset2",
            4,
        )

        assert job.status == JobStatus.IN_PROGRESS

        # WHEN
        self.job_service.fail(job, ["error1", "error2"])

        # THEN
        assert job.status == JobStatus.FAILED
        assert job.errors == {"error1", "error2"}
        mock_update_job.assert_called_once_with(job)
