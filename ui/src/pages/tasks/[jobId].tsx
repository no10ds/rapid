import ErrorCard from '@/components/ErrorCard/ErrorCard'
import AccountLayout from '@/components/Layout/AccountLayout'
import SimpleTable from '@/components/SimpleTable/SimpleTable'
import { asVerticalTableList } from '@/lib'
import { getJob } from '@/service'
import { Card, Typography, LinearProgress } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'

function GetJob() {
  const router = useRouter()
  const { jobId } = router.query
  const { isLoading, data, error } = useQuery(['getJob', jobId], getJob)

  if (isLoading) {
    return <LinearProgress />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  const renderErrors = () => {
    if (data.errors) {
      if ((data.errors as string[]).length) {
        return (
          <>
            <Typography variant="h2" gutterBottom>
              Errors
            </Typography>
            {(data.errors as string[]).map((error, index) => (
              <Typography variant="body2" color="error" component="code" key={index}>
                {error}
              </Typography>
            ))}
          </>
        )
      }
    }
    return null
  }

  return (
    <Card>
      <Typography variant="h2" gutterBottom>
        Job Detail
      </Typography>

      <Typography gutterBottom>Status - {data.status}</Typography>
      <Typography gutterBottom>ID - {data.job_id}</Typography>

      <SimpleTable
        list={asVerticalTableList([
          { name: 'Job Type', value: data.type as string },
          { name: 'Status', value: data.status as string },
          { name: 'Step', value: data.step as string },
          { name: 'Filename', value: data.filename as string },
          { name: 'Raw Filename	', value: data.raw_file_identifier as string },
          { name: 'Domain	', value: data.domain as string },
          { name: 'Dataset	', value: data.dataset as string },
          { name: 'Version	', value: data.version.toString() }
        ])}
      />

      {renderErrors()}
    </Card>
  )
}

export default GetJob

GetJob.getLayout = (page) => <AccountLayout title="Task Status">{page}</AccountLayout>
