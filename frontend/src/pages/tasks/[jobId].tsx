import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getJob } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { ReactNode } from 'react'
import Link from 'next/link'
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Alert,
  AlertTitle,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Stack
} from '@mui/material'

function statusChip(status: string) {
  if (status === 'SUCCESS') return <Chip size="small" label="Success" color="success" variant="outlined" />
  if (status === 'IN PROGRESS') return <Chip size="small" label="In Progress" color="warning" variant="outlined" />
  if (status === 'FAILED') return <Chip size="small" label="Failed" color="error" variant="outlined" />
  return <Chip size="small" label={status} variant="outlined" />
}

function formatTs(ts: number | string | undefined): string | null {
  if (!ts) return null
  const n = typeof ts === 'string' ? parseInt(ts, 10) : ts
  if (!n || isNaN(n)) return null
  return new Date(n * 1000).toLocaleString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

type ParsedError = {
  title: string
  detail: string
}

function parseError(raw: string): ParsedError {
  const colMismatch = raw.match(/Expected columns:\s*(\[[\s\S]*?\]),\s*received:\s*(\[[\s\S]*?\])/)
  if (colMismatch) {
    return {
      title: 'Column mismatch — your file does not match the schema',
      detail: `The schema expects columns ${colMismatch[1]} but your file contains ${colMismatch[2]}. Check that all required columns are present and no extra columns have been added.`
    }
  }

  const dateFormat = raw.match(/Column \[(.+?)\] does not match specified date format/)
  if (dateFormat) {
    return {
      title: `Invalid date format in column "${dateFormat[1]}"`,
      detail: `At least one value in the "${dateFormat[1]}" column does not match the date format required by the schema. Check that all dates in this column are consistently formatted.`
    }
  }

  const dataType = raw.match(/Column \[(.+?)\] has an incorrect data type\. Expected (.+?), received (.+)/)
  if (dataType) {
    return {
      title: `Wrong data type in column "${dataType[1]}"`,
      detail: `The schema expects "${dataType[1]}" to contain ${dataType[2]} values, but your file contains ${dataType[3]} values. Check that the column contains the correct type of data.`
    }
  }

  const partition = raw.match(/Partition column \[(.+?)\] has values with illegal characters/)
  if (partition) {
    return {
      title: `Illegal character in partition column "${partition[1]}"`,
      detail: `Values in the "${partition[1]}" column contain a "/" character, which is not allowed in partition columns. Remove or replace any forward slashes in this column.`
    }
  }

  if (/dataset has no rows/i.test(raw)) {
    return {
      title: 'File contains no data rows',
      detail: 'Your file appears to be empty or contains only a header row. Make sure your file has at least one data row before uploading.'
    }
  }

  const nullable = raw.match(/column\s*['""]?(.+?)['""]?\s+.*?null/i)
  if (nullable && /null/i.test(raw)) {
    const col = nullable[1].replace(/['"]/g, '').trim()
    return {
      title: `Missing values found in column "${col}"`,
      detail: `The "${col}" column has empty or null values, but the schema requires this column to always have a value. Fill in any blank cells in this column before re-uploading.`
    }
  }

  if (/unique/i.test(raw)) {
    const colMatch = raw.match(/column\s+['""]?(.+?)['""]?[\s,]/i)
    const col = colMatch ? colMatch[1].replace(/['"]/g, '').trim() : 'a column'
    return {
      title: `Duplicate values found in column "${col}"`,
      detail: `The "${col}" column must contain unique values, but duplicate entries were found. Remove duplicates before re-uploading.`
    }
  }

  return {
    title: 'Validation error',
    detail: raw
  }
}

function GetJob() {
  const router = useRouter()
  const { jobId } = router.query
  const { isLoading, data, error } = useQuery(['getJob', jobId], getJob)

  if (isLoading) return <LinearProgress color="primary" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  const errors: string[] = Array.isArray(data.errors)
    ? (data.errors as string[])
    : data.errors
      ? [String(data.errors)]
      : []

  const parsedErrors = errors.map(parseError)
  const hasFailed = data.status === 'FAILED'
  const createdAtStr = formatTs(data.createdat as number | string | undefined)

  const metaRows: [string, ReactNode][] = [
    ['Job ID', <Box key="id" component="span" sx={{ fontFamily: 'monospace', fontSize: 12, userSelect: 'all' }}>{data.job_id as string}</Box>],
    ['Type', data.type as string],
    ...(data.filename ? [['File', <Box key="fn" component="span" sx={{ fontFamily: 'monospace', fontSize: 12 }}>{data.filename as string}</Box>] as [string, ReactNode]] : []),
    ['Dataset', `${data.domain} / ${data.dataset}`],
    ['Layer', data.layer as string],
    ['Version', String(data.version)],
    ...(createdAtStr ? [['Started', createdAtStr] as [string, ReactNode]] : []),
  ]

  return (
    <Box sx={{ maxWidth: 860, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <FormCard
        title="Job Detail"
        headerAction={statusChip(data.status as string)}
        bodySx={{ p: 0 }}
      >
        <TableContainer>
          <Table size="small">
            <TableBody>
              {metaRows.map(([k, v]) => (
                <TableRow key={k as string}>
                  <TableCell sx={{ width: 140, fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.04em', color: 'text.disabled', whiteSpace: 'nowrap' }}>
                    {k}
                  </TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{v}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </FormCard>

      {hasFailed && parsedErrors.length > 0 && (
        <FormCard
          title={
            <Box sx={{ color: 'error.main' }}>
              <Box>
                {parsedErrors.length === 1 && parsedErrors[0].title !== 'Validation error'
                  ? parsedErrors[0].title
                  : "Your file didn't pass validation"}
              </Box>
              <Typography sx={{ fontSize: 12, fontWeight: 400, color: 'error.main', mt: 0.5 }}>
                No data was written. Fix the issues below, then re-upload.
              </Typography>
            </Box>
          }
          headerAction={
            <Chip
              size="small"
              color="error"
              variant="outlined"
              label={`${parsedErrors.length} error${parsedErrors.length !== 1 ? 's' : ''}`}
            />
          }
        >
          <Stack spacing={1.5}>
            <Stack spacing={1}>
              {parsedErrors.map((e, i) => (
                <Alert key={i} severity="error" variant="outlined">
                  <AlertTitle sx={{ fontSize: 12, fontWeight: 600 }}>{e.title}</AlertTitle>
                  <Typography sx={{ fontSize: 12 }}>{e.detail}</Typography>
                </Alert>
              ))}
            </Stack>

            <Box sx={{ borderTop: '1px solid', borderColor: 'divider', pt: 2 }}>
              <Typography sx={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: 'text.disabled', mb: 1 }}>
                What would you like to do?
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 1.5 }}>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Typography sx={{ fontSize: 13, fontWeight: 600, mb: 0.5 }}>Fix my file</Typography>
                  <Typography sx={{ fontSize: 12, color: 'text.secondary', mb: 1.5 }}>
                    Update the values in your file to match what the schema expects, then re-upload.
                  </Typography>
                  <Button component={Link} href="/data/upload" size="small" variant="contained">
                    ↑ Upload again
                  </Button>
                </Paper>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Typography sx={{ fontSize: 13, fontWeight: 600, mb: 0.5 }}>Update the schema</Typography>
                  <Typography sx={{ fontSize: 12, color: 'text.secondary', mb: 1.5 }}>
                    If your file is correct, delete the existing dataset first, then create a new schema and re-upload. Requires Data Admin permissions.
                  </Typography>
                  <Button component={Link} href="/catalog" size="small" variant="outlined">
                    Go to Catalog →
                  </Button>
                </Paper>
              </Box>
            </Box>
          </Stack>
        </FormCard>
      )}

      {!hasFailed && (
        <Box>
          <Button component={Link} href="/tasks" size="small">
            ← Back to Jobs
          </Button>
        </Box>
      )}
    </Box>
  )
}

export default GetJob

GetJob.getLayout = (page: ReactNode) => (
  <AccountLayout title="Job Detail">{page}</AccountLayout>
)
