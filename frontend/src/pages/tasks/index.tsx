import { Card, Link, SimpleTable, AccountLayout } from '@/components'
import { getAllJobs } from '@/service'
import {
  Box,
  InputAdornment,
  LinearProgress,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import CancelIcon from '@mui/icons-material/Cancel'
import QueryBuilderIcon from '@mui/icons-material/QueryBuilder'
import SearchIcon from '@mui/icons-material/Search'
import ErrorCard from '@/components/ErrorCard/ErrorCard'

type StatusFilter = 'ALL' | 'IN PROGRESS' | 'SUCCESS' | 'FAILED'

function getStatusSymbol(status: string) {
  if (status === 'SUCCESS') return <CheckCircleOutlineIcon color="success" />
  else if (status === 'IN PROGRESS') return <QueryBuilderIcon />
  else if (status === 'FAILED') return <CancelIcon color="error" />
  return null
}

function StatusPage() {
  const { isLoading, data, error } = useQuery(['jobs'], getAllJobs)
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL')
  const [typeFilter, setTypeFilter] = useState('')

  if (isLoading) return <LinearProgress />
  if (error) return <ErrorCard error={error as Error} />

  const hasCreatedAt = data.some((j) => j.created_at)

  const filtered = data
    .filter((job) => statusFilter === 'ALL' || job.status === statusFilter)
    .filter(
      (job) =>
        !typeFilter ||
        String(job.type ?? '').toLowerCase().includes(typeFilter.toLowerCase())
    )

  const headers = [
    { children: 'Type' },
    { children: 'Layer' },
    { children: 'Domain' },
    { children: 'Dataset' },
    { children: 'Version' },
    { children: 'Status' },
    { children: 'Step' },
    { children: 'Job ID' },
    { children: '' },
    ...(hasCreatedAt ? [{ children: 'Created At' }] : [])
  ]

  const list = filtered.map((job) => [
    { children: <>{job.type}</> },
    { children: <>{job.layer}</> },
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
    },
    ...(hasCreatedAt ? [{ children: <>{job.created_at ?? ''}</> }] : [])
  ])

  return (
    <Card data-testid="tasks-content">
      <Typography variant="body1" gutterBottom>
        View all the tracked asynchronous processing jobs and the status of each job.
        Press the desired job id to get greater details on its run.
      </Typography>

      <Typography variant="h2" gutterBottom>
        Jobs
      </Typography>

      <Box
        sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2, flexWrap: 'wrap' }}
      >
        <ToggleButtonGroup
          value={statusFilter}
          exclusive
          size="small"
          onChange={(_e, value) => {
            if (value !== null) setStatusFilter(value as StatusFilter)
          }}
          aria-label="Status filter"
        >
          {(['ALL', 'IN PROGRESS', 'SUCCESS', 'FAILED'] as StatusFilter[]).map((s) => (
            <ToggleButton key={s} value={s}>
              {s}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>

        <TextField
          size="small"
          placeholder="Filter by type"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            )
          }}
          sx={{ minWidth: 200 }}
        />
      </Box>

      <SimpleTable list={list} headers={headers} />
    </Card>
  )
}

export default StatusPage

StatusPage.getLayout = (page) => <AccountLayout title="Task Status">{page}</AccountLayout>
