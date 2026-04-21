import ErrorCard from '@/components/ErrorCard/ErrorCard'
import AccountLayout from '@/components/Layout/AccountLayout'
import { Card, Link, SimpleTable } from '@/components'
import { asVerticalTableList } from '@/utils'
import { getJob } from '@/service'
import {
  Box,
  Button,
  Chip,
  LinearProgress,
  Stack,
  Typography
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'

function parseFriendlyError(rawError: string): string {
  const lower = rawError.toLowerCase()
  if (lower.includes('expected columns') || lower.includes('received')) {
    return 'The columns in your file do not match the schema. Check your column names match exactly.'
  }
  if (lower.includes('null')) {
    return 'Your file contains empty values in a column that does not allow nulls.'
  }
  if (lower.includes('invalid date') || lower.includes('date format')) {
    return 'One or more date values in your file are in the wrong format.'
  }
  if (lower.includes('invalid value') || lower.includes('expected one of')) {
    return 'Your file contains values that do not match the allowed options in the schema.'
  }
  return rawError
}

function statusBadgeColor(
  status: string
): 'success' | 'error' | 'warning' | 'default' {
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAILED') return 'error'
  if (status === 'IN PROGRESS') return 'warning'
  return 'default'
}

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

  const status = data.status as string
  const errors = Array.isArray(data.errors) ? (data.errors as string[]) : []
  const hasErrors = errors.length > 0

  const detailRows = asVerticalTableList([
    { name: 'Job ID', value: String(data.job_id ?? '') },
    { name: 'Type', value: String(data.type ?? '') },
    { name: 'File', value: String(data.filename ?? '') },
    {
      name: 'Dataset',
      value: [data.domain, data.dataset].filter(Boolean).join('/')
    },
    { name: 'Layer', value: String(data.layer ?? '') },
    { name: 'Version', value: String(data.version ?? '') },
    ...(data.created_at ? [{ name: 'Started', value: String(data.created_at) }] : [])
  ])

  return (
    <Box sx={{ maxWidth: 860, mx: 'auto' }}>
      <Box sx={{ mb: 2 }}>
        <Link href="/tasks">← Jobs</Link>
      </Box>

      <Card sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Typography variant="h2">Job Detail</Typography>
          <Chip
            label={status}
            color={statusBadgeColor(status)}
            size="small"
          />
        </Box>

        <SimpleTable list={detailRows} />
      </Card>

      {hasErrors && (
        <Card>
          <Typography variant="h2" gutterBottom>
            Errors
          </Typography>

          <Stack spacing={1} sx={{ mb: 3 }}>
            {errors.map((rawError, index) => (
              <Typography
                key={index}
                variant="body2"
                color="error"
                component="p"
              >
                {parseFriendlyError(rawError)}
              </Typography>
            ))}
          </Stack>

          <Typography variant="h3" gutterBottom>
            What would you like to do?
          </Typography>

          <Stack spacing={3}>
            <Box>
              <Typography variant="h3" gutterBottom>
                Fix my file
              </Typography>
              <Typography variant="body2" gutterBottom>
                Correct the issues in your file and upload it again.
              </Typography>
              <Button variant="contained" color="primary" href="/data/upload/">
                Upload again
              </Button>
            </Box>

            <Box>
              <Typography variant="h3" gutterBottom>
                Update schema
              </Typography>
              <Typography variant="body2">
                If your file is correct and the schema needs updating: first delete the
                existing data, then update the schema and re-upload your file. This
                action requires schema management permissions.
              </Typography>
            </Box>
          </Stack>
        </Card>
      )}
    </Box>
  )
}

export default GetJob

GetJob.getLayout = (page) => <AccountLayout title="Task Status">{page}</AccountLayout>
