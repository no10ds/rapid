import { UploadDatasetResponseDetails } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { getJob } from '@/service'
import { useState, Dispatch, SetStateAction } from 'react'
import { useRouter } from 'next/router'

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
    <div data-testid="upload-status">
      <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 8 }}>
        Processing {uploadSuccessDetails.original_filename}…
      </div>
      <div className="rapid-loading-bar" role="progressbar" />
    </div>
  )
}

export default UploadProgress
