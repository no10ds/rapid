import { Alert, AlertColor, LinearProgress, Link, Typography } from '@mui/material'
import { UploadDatasetResponseDetails } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { getJob } from '@/service'
import { useState, Dispatch, SetStateAction } from 'react'
import Row from '../Row'

enum UploadStatus {
    Failed = "FAILED",
    Success = "SUCCESS",
    InProgress = "IN PROGRESS",
}

const statusConverter = {
    [UploadStatus.Failed]: {
        severity: "error",
        message: "Data upload error",
        link: "See error details"
    },
    [UploadStatus.Success]: {
        severity: "success",
        message: "Data uploaded successfully",
        link: "See upload details"
    },
    [UploadStatus.InProgress]: {
        severity: "info",
        message: "Data processing",
        link: "See progress details"
    },
}


const UploadProgress = ({ uploadSuccessDetails, setDisableUpload }: { uploadSuccessDetails: UploadDatasetResponseDetails, setDisableUpload: Dispatch<SetStateAction<boolean>> }) => {

    const [stop, setStop] = useState(false);
    const [status, setStatus] = useState<UploadStatus>(UploadStatus.InProgress);

    useQuery(['getJob', uploadSuccessDetails.job_id], getJob, {
        onSuccess: data => {
            switch (data.status) {
                case UploadStatus.Success:
                case UploadStatus.Failed:
                    setStop(true);
                    setStatus(data.status)
                    setDisableUpload(false)
                    break
                default:
                    break;
            }
        },
        // Keep refetching every second
        refetchInterval: stop ? false : 1000,
        refetchIntervalInBackground: true,
        refetchOnWindowFocus: false,
    });

    return (
        <Alert
            title={`File accepted: ${uploadSuccessDetails.original_filename}`}
            data-testid="upload-status"
            severity={statusConverter[status].severity as AlertColor}
        >
            <Typography variant="caption">Status: {statusConverter[status].message}</Typography>
            {!stop &&
                <div style={{ padding: '15px 0px' }}>
                    <LinearProgress />
                </div>
            }
            <Row>
                <Link sx={{ pt: 5 }} href={`/tasks/${uploadSuccessDetails.job_id}`}>
                    {statusConverter[status].link}
                </Link>
            </Row>
        </Alert >
    )
}

export default UploadProgress;