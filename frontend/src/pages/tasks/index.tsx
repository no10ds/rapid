import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import StatusChip from '@/components/Chip/StatusChip'
import { formatTs } from '@/utils/date'
import { getAllJobs } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { ReactNode, useState, useMemo } from 'react'
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Typography,
  LinearProgress,
  Button
} from '@mui/material'
import Link from 'next/link'


type TypeFilter = 'All' | 'UPLOAD' | 'QUERY'

function StatusPage() {
  const { isLoading, data, error } = useQuery(['jobs'], getAllJobs)
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('All')

  const typeFilters: TypeFilter[] = ['All', 'UPLOAD', 'QUERY']

  const filtered = useMemo(() => {
    if (!data) return []
    if (typeFilter === 'All') return data
    return data.filter((job) => (job.type as string)?.toUpperCase() === typeFilter)
  }, [data, typeFilter])

  const hasCreatedAt = useMemo(
    () => filtered.some((job) => job.createdat != null),
    [filtered]
  )

  if (isLoading) return <LinearProgress color="primary" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  return (
    <Paper variant="outlined" data-testid="tasks-content">
      {/* Toolbar */}
      <Box sx={{ px: '18px', py: '14px', display: 'flex', gap: '10px', borderBottom: '1px solid', borderColor: 'divider' }}>
        {typeFilters.map((f) => (
          <Chip
            key={f}
            label={f}
            size="small"
            variant={typeFilter === f ? 'filled' : 'outlined'}
            color={typeFilter === f ? 'primary' : 'default'}
            onClick={() => setTypeFilter(f)}
          />
        ))}
      </Box>

      {/* Table */}
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Job ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Layer</TableCell>
              <TableCell>Domain</TableCell>
              <TableCell>Dataset</TableCell>
              <TableCell>Version</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Step</TableCell>
              {hasCreatedAt && <TableCell>Created At</TableCell>}
              <TableCell></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={hasCreatedAt ? 10 : 9} sx={{ textAlign: 'center', py: 5, color: 'text.disabled', fontSize: 13 }}>
                  No {typeFilter !== 'All' ? typeFilter.toLowerCase() : ''} jobs found.
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((job, idx) => {
                const createdAtStr = formatTs(job.createdat as number | string | undefined)
                return (
                  <TableRow key={idx} hover>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                      <Link href={`/tasks/${job.job_id}`} style={{ color: '#ec4899', textDecoration: 'none' }}>
                        {job.job_id}
                      </Link>
                    </TableCell>
                    <TableCell>{job.type}</TableCell>
                    <TableCell>{job.layer}</TableCell>
                    <TableCell>{job.domain}</TableCell>
                    <TableCell sx={{ fontWeight: 500 }}>{job.dataset}</TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{job.version}</TableCell>
                    <TableCell><StatusChip status={job.status as string} /></TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{job.step}</TableCell>
                    {hasCreatedAt && (
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{createdAtStr ?? '—'}</TableCell>
                    )}
                    <TableCell>
                      {job.status === 'FAILED' && (
                        <Button
                          component={Link}
                          href={`/tasks/${job.job_id}`}
                          size="small"
                          color="error"
                          variant="outlined"
                          sx={{ fontSize: 11 }}
                        >
                          Details
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Footer */}
      <Box sx={{ px: '18px', py: '12px', borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="body2" sx={{ fontSize: 12 }}>
          {filtered.length} job{filtered.length !== 1 ? 's' : ''}
          {typeFilter !== 'All' ? ` (${typeFilter.toLowerCase()})` : ''}
        </Typography>
      </Box>
    </Paper>
  )
}

export default StatusPage

StatusPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Jobs">{page}</AccountLayout>
)
