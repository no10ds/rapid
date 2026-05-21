import { UploadDatasetResponseDetails } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { getJob } from '@/service'
import { useState, Dispatch, SetStateAction } from 'react'
import { useRouter } from 'next/router'
import { Box, Typography, LinearProgress } from '@mui/material'

const UploadProgress = ({
  uploadSuccessDetails,
  setDisableUpload
}: {
  uploadSuccessDetails: UploadDatasetResponseDetails
  setDisableUpload: Dispatch<SetStateAction<boolean>>
}) => {
  const router = useRouter()
  const [stop, setStop] = useState(false)

  useQuery(['getJob', uploadSuccessDetails.job_id], getJob, {
    onSuccess: (data) => {
      if (data.status === 'SUCCESS' || data.status === 'FAILED') {
        setStop(true)
        setDisableUpload(false)
        router.push(`/tasks/${uploadSuccessDetails.job_id}`)
      }
    },
    refetchInterval: stop ? false : 1000,
    refetchIntervalInBackground: true,
    refetchOnWindowFocus: false
  })

  return (
    <Box data-testid="upload-status">
      <Typography sx={{ fontSize: 13, fontWeight: 500, color: 'text.secondary', mb: 1 }}>
        Processing {uploadSuccessDetails.original_filename}…
      </Typography>
      <LinearProgress color="primary" role="progressbar" />
    </Box>
  )
}

export default UploadProgress
