from unittest.mock import patch

from api.domain.Jobs.Job import JobType, JobStatus
from api.domain.Jobs.UploadJob import UploadJob, UploadStep


@patch("api.domain.Jobs.UploadJob.time")
def test_initialise_upload_job(mock_time):
    mock_time.time.return_value = 1000

    job = UploadJob(
        "subject-123",
        "abc-123",
        "some-filename.csv",
        "111-222-333",
        "domain1",
        "dataset2",
        12,
    )

    assert job.job_id == "abc-123"
    assert job.job_type == JobType.UPLOAD
    assert job.status == JobStatus.IN_PROGRESS
    assert job.step == UploadStep.INITIALISATION
    assert job.errors == set()
    assert job.filename == "some-filename.csv"
    assert job.raw_file_identifier == "111-222-333"
    assert job.subject_id == "subject-123"
    assert job.domain == "domain1"
    assert job.dataset == "dataset2"
    assert job.version == 12
    assert job.expiry_time == 605800
