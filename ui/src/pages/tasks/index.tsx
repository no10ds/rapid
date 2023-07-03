import { Card, Link, SimpleTable, AccountLayout } from '@/components'
import { getAllJobs } from '@/service'
import { Typography, LinearProgress } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import CancelIcon from '@mui/icons-material/Cancel'
import QueryBuilderIcon from '@mui/icons-material/QueryBuilder'
import ErrorCard from '@/components/ErrorCard/ErrorCard'

function getStatusSymbol(status: string) {
  if (status === 'SUCCESS') return <CheckCircleOutlineIcon color="success" />
  else if (status === 'IN PROGRESS') return <QueryBuilderIcon />
  else if (status === 'FAILED') return <CancelIcon color="error" />
}

function StatusPage() {
  const { isLoading, data, error } = useQuery(['jobs'], getAllJobs)

  if (isLoading) {
    return <LinearProgress />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  return (
    <Card data-testid="tasks-content">
      <Typography variant="body1" gutterBottom>
        View all the tracked asynchronous processing jobs and the status of each job.
        Press the desired job id to get greater details on it's run.
      </Typography>

      <Typography variant="h2" gutterBottom>
        Jobs
      </Typography>

      <SimpleTable
        list={data.map((job) => {
          return [
            { children: <>{job.type}</> },
            { children: <>{job.domain}</> },
            { children: <>{job.dataset}</> },
            { children: <>{job.version}</> },
            { children: getStatusSymbol(job.status as string) },
            { children: <>{job.step}</> },
            {
              children: (
                <Link color="inherit" href={`tasks/${job.job_id}`}>
                  {job.job_id}
                </Link>
              )
            },
            {
              children:
                job.status === 'FAILED' ? (
                  <Link href={`tasks/${job.job_id}`}>Failure Details</Link>
                ) : (
                  <></>
                )
            }
          ]
        })}
        headers={[
          { children: 'Type' },
          { children: 'Domain' },
          { children: 'Dataset' },
          { children: 'Version' },
          { children: 'Status' },
          { children: 'Step' },
          { children: 'Job ID' },
          { children: '' }
        ]}
      />
    </Card>
  )
}

export default StatusPage

StatusPage.getLayout = (page) => <AccountLayout title="Task Status">{page}</AccountLayout>
