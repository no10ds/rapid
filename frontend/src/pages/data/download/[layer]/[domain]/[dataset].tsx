import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { formatDate } from '@/utils/date'
import { triggerBlobDownload } from '@/utils/download'
import { buildQueryPayload } from '@/utils/query'
import { getDatasetInfo, queryDataset } from '@/service'
import { DataFormats } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'
import Link from 'next/link'
import {
  Box,
  Typography,
  Button,
  Chip,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField
} from '@mui/material'

function DownloadDataset() {
  const router = useRouter()
  const { layer, domain, dataset } = router.query
  const version = router.query.version ? router.query.version : 0
  const [dataFormat, setDataFormat] = useState<DataFormats>('csv')
  const [queryBody, setQueryBody] = useState({
    select_columns: '',
    filter: '',
    group_by_columns: '',
    aggregation_conditions: '',
    limit: ''
  })
  const [noContentReturn, setNoContentReturn] = useState(false)

  const {
    isLoading: isDatasetInfoLoading,
    data: datasetInfoData,
    error: datasetInfoError
  } = useQuery(
    ['datasetInfo', layer, domain, dataset, version ? version : 0],
    getDatasetInfo
  )

  const { isLoading, mutate, error } = useMutation<
    Response,
    Error,
    { path: string; dataFormat: DataFormats; data: unknown }
  >({
    mutationFn: queryDataset,
    onSuccess: async (response, { dataFormat: fmt }) => {
      if (response.status === 200) {
        setNoContentReturn(false)
        triggerBlobDownload(await response.blob(), `${layer}_${domain}_${dataset}_${version}.${fmt}`)
      } else if (response.status === 204) {
        setNoContentReturn(true)
      }
    }
  })

  if (isDatasetInfoLoading) {
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (datasetInfoError) {
    return <ErrorCard error={datasetInfoError as Error} />
  }

const overviewRows: [string, string][] = [
    ['Domain', domain as string],
    ['Dataset', dataset as string],
    ['Description', datasetInfoData.metadata.description],
    ['Version', version as string],
    ['Last updated', formatDate(datasetInfoData.metadata.last_updated)],
    ['Last uploaded by', datasetInfoData.metadata.last_uploaded_by || 'Unknown'],
    ['Number of rows', datasetInfoData.metadata.number_of_rows?.toString()],
    ['Number of columns', datasetInfoData.metadata.number_of_columns?.toString()]
  ]

  const queryFields = [
    { key: 'select_columns', label: 'Select Columns', placeholder: 'column1, avg(column2)' },
    { key: 'filter', label: 'Filter', placeholder: 'column >= 10' },
    { key: 'group_by_columns', label: 'Group by Columns', placeholder: 'column1, column3' },
    {
      key: 'aggregation_conditions',
      label: 'Aggregation Conditions',
      placeholder: 'avg(column2) <= 15'
    },
    { key: 'limit', label: 'Row Limit', placeholder: '30' }
  ] as const

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <FormCard num={1} title="Dataset overview" bodySx={{ p: 0 }}>
        <TableContainer>
          <Table size="small">
            <TableBody>
              {overviewRows.map(([k, v]) => (
                <TableRow key={k}>
                  <TableCell sx={{ width: 200, fontWeight: 600, color: 'text.disabled', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                    {k}
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{v}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </FormCard>

      <FormCard num={2} title="Columns" bodySx={{ p: 0 }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Data Type</TableCell>
                <TableCell>Allows Null</TableCell>
                <TableCell>Is Unique</TableCell>
                <TableCell>Max</TableCell>
                <TableCell>Min</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {datasetInfoData.columns.map((column, idx) => (
                <TableRow key={idx}>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{column.name}</TableCell>
                  <TableCell>{column.data_type}</TableCell>
                  <TableCell>{column.allow_null ? 'Yes' : 'No'}</TableCell>
                  <TableCell>{column.unique ? 'Yes' : 'No'}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>
                    {column.statistics ? column.statistics.max : '—'}
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>
                    {column.statistics ? column.statistics.min : '—'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </FormCard>

      <FormCard num={3} title="Query" optional>
        <Typography variant="body2" sx={{ fontSize: 12, mb: 2 }}>
          For further information on writing queries consult the{' '}
          <Box
            component="a"
            href="https://rapid.readthedocs.io/en/latest/api/query/"
            target="_blank"
            rel="noreferrer"
            sx={{ color: 'primary.main', textDecoration: 'none' }}
          >
            query writing guide
          </Box>
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {queryFields.map(({ key, label, placeholder }) => (
            <TextField
              key={key}
              size="small"
              label={label}
              placeholder={placeholder}
              value={queryBody[key as keyof typeof queryBody]}
              onChange={(e) => setQueryBody({ ...queryBody, [key]: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          ))}
        </Box>
      </FormCard>

      <FormCard
        num={4}
        title="Output format"
        actions={
          <>
            <Button
              variant="contained"
              disabled={isLoading}
              onClick={() =>
                mutate({
                  path: `${layer}/${domain}/${dataset}/query?version=${version}`,
                  dataFormat,
                  data: buildQueryPayload(queryBody)
                })
              }
            >
              {isLoading ? 'Downloading…' : 'Download'}
            </Button>
            <Button variant="outlined" component={Link} href="/data/download">
              Back
            </Button>
          </>
        }
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          {(['csv', 'json'] as DataFormats[]).map((fmt) => (
            <Chip
              key={fmt}
              label={fmt.toUpperCase()}
              size="small"
              onClick={() => setDataFormat(fmt)}
              variant={dataFormat === fmt ? 'filled' : 'outlined'}
              color={dataFormat === fmt ? 'primary' : 'default'}
            />
          ))}
        </Box>
      </FormCard>

      {noContentReturn && (
        <Alert severity="warning" variant="outlined">
          No data returned for this query. Please ensure that data has been uploaded and the
          query is not too restrictive.
        </Alert>
      )}
      {error && <Alert severity="error" variant="outlined">{error?.message}</Alert>}
    </Box>
  )
}

export default DownloadDataset

DownloadDataset.getLayout = (page: ReactNode) => (
  <AccountLayout title="Download">{page}</AccountLayout>
)
