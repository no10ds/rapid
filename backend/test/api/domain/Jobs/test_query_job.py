from unittest.mock import patch

from api.domain.Jobs.Job import JobType, JobStatus
from api.domain.Jobs.QueryJob import QueryJob, QueryStep
from api.domain.dataset_metadata import DatasetMetadata


@patch("api.domain.Jobs.Job.uuid")
@patch("api.domain.Jobs.QueryJob.time")
def test_initialise_query_job(mock_time, mock_uuid):
    mock_time.time.return_value = 1000
    mock_uuid.uuid4.return_value = "abc-123"
    version = 9

    job = QueryJob(
        "subject-123", DatasetMetadata("layer", "domain1", "dataset1", version)
    )

    assert job.job_id == "abc-123"
    assert job.job_type == JobType.QUERY
    assert job.status == JobStatus.IN_PROGRESS
    assert job.step == QueryStep.INITIALISATION
    assert job.errors == set()
    assert job.subject_id == "subject-123"
    assert job.domain == "domain1"
    assert job.dataset == "dataset1"
    assert job.layer == "layer"
    assert job.version == 9
    assert job.results_url is None
    assert job.expiry_time == 87400
