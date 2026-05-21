import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import UploadProgress from '@/components/UploadProgress/UploadProgress'
import { getDatasetInfo, getMethods, queryDataset, uploadDataset } from '@/service'
import { DataFormats, UploadDatasetResponse, UploadDatasetResponseDetails } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'
import {
  Box,
  Paper,
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
  TextField,
  Stack
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'

type ActiveTab = 'download' | 'upload' | null

function formatDate(raw: string | undefined): string {
  if (!raw) return '—'
  const d = new Date(raw)
  if (isNaN(d.getTime())) return raw
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

function layerColor(layer: string): 'info' | 'success' | 'warning' | 'default' {
  switch (layer?.toLowerCase()) {
    case 'raw': return 'info'
    case 'curated': return 'success'
    case 'processed': return 'warning'
    default: return 'default'
  }
}

function DatasetDetailPage() {
  const router = useRouter()
  const { layer, domain, dataset } = router.query
  const version = router.query.version ? router.query.version : 0
  const [activeTab, setActiveTab] = useState<ActiveTab>(null)
  const [dataFormat, setDataFormat] = useState<DataFormats>('csv')
  const [showQuery, setShowQuery] = useState(false)
  const [queryBody, setQueryBody] = useState({
    select_columns: '',
    filter: '',
    group_by_columns: '',
    aggregation_conditions: '',
    limit: ''
  })
  const [noContentReturn, setNoContentReturn] = useState(false)
  const [uploadFile, setUploadFile] = useState<File | undefined>()
  const [uploadDetails, setUploadDetails] = useState<UploadDatasetResponseDetails | undefined>()
  const [uploadDisable, setUploadDisable] = useState(false)

  const { data: methods } = useQuery({
    queryKey: ['methods'],
    queryFn: getMethods
  })

  const {
    isLoading,
    data: info,
    error
  } = useQuery(
    ['datasetInfo', layer, domain, dataset, version ? version : 0],
    getDatasetInfo,
    { enabled: !!layer && !!domain && !!dataset }
  )

  const { isLoading: isDownloading, mutate, error: downloadError } = useMutation<
    Response,
    Error,
    { path: string; dataFormat: DataFormats; data: unknown }
  >({
    mutationFn: queryDataset,
    onSuccess: async (response, { dataFormat: fmt }) => {
      if (response.status === 200) {
        setNoContentReturn(false)
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `${layer}_${domain}_${dataset}_${version}.${fmt}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
      } else if (response.status === 204) {
        setNoContentReturn(true)
      }
    }
  })

  const { isLoading: isUploading, mutate: mutateUpload, error: uploadError } = useMutation<
    UploadDatasetResponse,
    Error,
    { path: string; data: FormData }
  >({
    mutationFn: uploadDataset,
    onMutate: () => setUploadDetails(undefined),
    onSuccess: (data) => {
      setUploadDetails(data.details)
      setUploadDisable(true)
    }
  })

  if (isLoading) {
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  if (!info) return null

  const meta = info.metadata

  const createQueryBodyData = () => {
    const queryBodyData: Record<string, unknown> = {}
    if (queryBody.select_columns) queryBodyData.select_columns = queryBody.select_columns.split(',')
    if (queryBody.filter) queryBodyData.filter = queryBody.filter
    if (queryBody.group_by_columns) queryBodyData.group_by_columns = queryBody.group_by_columns.split(',')
    if (queryBody.aggregation_conditions) queryBodyData.aggregation_conditions = queryBody.aggregation_conditions
    if (queryBody.limit) queryBodyData.limit = queryBody.limit
    return queryBodyData
  }

  const tags = [
    ...(meta.key_only_tags || []),
    ...Object.entries(meta.key_value_tags || {}).map(([k, v]) => `${k}: ${v}`)
  ]

  const queryFields = [
    { key: 'select_columns', label: 'Select Columns', placeholder: 'column1, avg(column2)' },
    { key: 'filter', label: 'Filter', placeholder: 'column >= 10' },
    { key: 'group_by_columns', label: 'Group by Columns', placeholder: 'column1, column3' },
    { key: 'aggregation_conditions', label: 'Aggregation Conditions', placeholder: 'avg(column2) <= 15' },
    { key: 'limit', label: 'Row Limit', placeholder: '30' }
  ] as const

  const stats: [string, string][] = [
    ['Rows', meta.number_of_rows?.toLocaleString() ?? '—'],
    ['Columns', meta.number_of_columns?.toLocaleString() ?? '—'],
    ['Version', String(version)],
    ['Last Updated', formatDate(meta.last_updated)],
    ['Uploaded By', meta.last_uploaded_by || '—']
  ]

  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Stack direction="row" spacing={1} flexWrap="wrap">
        {methods?.can_download && (
          <Button
            variant={activeTab === 'download' ? 'contained' : 'outlined'}
            onClick={() => setActiveTab(activeTab === 'download' ? null : 'download')}
          >
            Download
          </Button>
        )}
        {methods?.can_upload && (
          <Button
            variant={activeTab === 'upload' ? 'contained' : 'outlined'}
            onClick={() => setActiveTab(activeTab === 'upload' ? null : 'upload')}
          >
            Upload
          </Button>
        )}
        {methods?.can_create_schema && (
          <Button
            variant="outlined"
            onClick={() => router.push(`/schema/edit/${layer}/${domain}/${dataset}?version=${version}`)}
          >
            Edit Schema
          </Button>
        )}
        {methods?.can_create_schema && (
          <Button
            variant="outlined"
            color="error"
            onClick={() => router.push({
              pathname: '/data/delete',
              query: { layer: layer as string, domain: domain as string, dataset: dataset as string }
            })}
          >
            Delete
          </Button>
        )}
      </Stack>

      {activeTab === 'download' && methods?.can_download && (
        <FormCard
          title="Download"
          actionsError={downloadError}
          actions={
            <Button
              variant="contained"
              disabled={isDownloading}
              onClick={() =>
                mutate({
                  path: `${layer}/${domain}/${dataset}/query?version=${version}`,
                  dataFormat,
                  data: createQueryBodyData()
                })
              }
            >
              {isDownloading ? 'Downloading…' : 'Download'}
            </Button>
          }
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="body2" sx={{ fontSize: 12 }}>Format:</Typography>
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

          <Button size="small" onClick={() => setShowQuery(!showQuery)} sx={{ mb: 1 }}>
            {showQuery ? 'Hide query options' : 'Show query options (optional)'}
          </Button>

          {showQuery && (
            <Box sx={{ mt: 2 }}>
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
            </Box>
          )}

          {noContentReturn && (
            <Alert severity="warning" variant="outlined" sx={{ mt: 2 }}>
              No data returned for this query. Please ensure that data has been uploaded and the
              query is not too restrictive.
            </Alert>
          )}
        </FormCard>
      )}

      {activeTab === 'upload' && methods?.can_upload && (
        <FormCard
          title="Upload"
          actionsError={uploadError}
          actions={
            <Button
              variant="contained"
              disabled={!uploadFile || isUploading || uploadDisable}
              onClick={() => {
                if (uploadFile) {
                  const formData = new FormData()
                  formData.append('file', uploadFile)
                  mutateUpload({
                    path: `${layer}/${domain}/${dataset}?version=${version}`,
                    data: formData
                  })
                }
              }}
            >
              {isUploading ? 'Uploading…' : 'Upload dataset'}
            </Button>
          }
        >
          {!uploadDisable && (
            <Box
              component="label"
              htmlFor="detail-upload-file"
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                p: 4,
                border: '2px dashed',
                borderColor: 'divider',
                borderRadius: 1,
                cursor: 'pointer',
                bgcolor: 'background.default',
                '&:hover': { borderColor: 'primary.main' }
              }}
            >
              <CloudUploadIcon sx={{ fontSize: 32, color: 'text.disabled' }} />
              <Typography sx={{ fontSize: 13, fontWeight: 500 }}>
                Drag &amp; drop your CSV file here
              </Typography>
              <Typography sx={{ fontSize: 11, color: 'text.disabled' }}>
                or click to browse — CSV only, max 100 MB
              </Typography>
              {uploadFile && (
                <Typography sx={{ fontSize: 12, color: 'primary.main', fontWeight: 500 }}>
                  {uploadFile.name}
                </Typography>
              )}
            </Box>
          )}
          <input
            id="detail-upload-file"
            type="file"
            style={{ display: 'none' }}
            onChange={(e) => setUploadFile(e.target.files?.[0])}
          />

          {uploadDetails && (
            <Box sx={{ mt: 2 }}>
              <UploadProgress
                uploadSuccessDetails={uploadDetails}
                setDisableUpload={setUploadDisable}
              />
            </Box>
          )}
        </FormCard>
      )}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
          <Typography variant="h1" sx={{ fontSize: 22, mr: 1 }}>{dataset}</Typography>
          <Chip size="small" label={layer as string} color={layerColor(layer as string)} variant="outlined" />
          {meta.sensitivity && <Chip size="small" label={meta.sensitivity} variant="outlined" />}
        </Stack>
        <Typography variant="body2" sx={{ fontSize: 12, color: 'text.secondary', mt: 0.5 }}>
          {layer} / {domain} / {dataset}
        </Typography>
        {meta.description && (
          <Typography variant="body1" sx={{ fontSize: 13, mt: 1.5 }}>{meta.description}</Typography>
        )}
      </Paper>

      <Paper variant="outlined" sx={{ p: 2, display: 'flex', gap: 4, flexWrap: 'wrap' }}>
        {stats.map(([label, value]) => (
          <Box key={label}>
            <Typography sx={{ fontSize: 18, fontWeight: 600 }}>{value}</Typography>
            <Typography sx={{ fontSize: 11, color: 'text.disabled', textTransform: 'uppercase', letterSpacing: '.05em' }}>
              {label}
            </Typography>
          </Box>
        ))}
      </Paper>

      {(meta.owners?.length || tags.length || meta.update_behaviour) ? (
        <Paper variant="outlined" sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
          {meta.update_behaviour && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography sx={{ fontSize: 11, fontWeight: 600, color: 'text.disabled', textTransform: 'uppercase', letterSpacing: '.05em', minWidth: 140 }}>
                Update Behaviour
              </Typography>
              <Typography sx={{ fontSize: 13 }}>{meta.update_behaviour}</Typography>
            </Box>
          )}
          {meta.owners && meta.owners.length > 0 && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography sx={{ fontSize: 11, fontWeight: 600, color: 'text.disabled', textTransform: 'uppercase', letterSpacing: '.05em', minWidth: 140 }}>
                Owners
              </Typography>
              <Typography sx={{ fontSize: 13 }}>
                {meta.owners.map((o) => `${o.name} (${o.email})`).join(', ')}
              </Typography>
            </Box>
          )}
          {tags.length > 0 && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography sx={{ fontSize: 11, fontWeight: 600, color: 'text.disabled', textTransform: 'uppercase', letterSpacing: '.05em', minWidth: 140 }}>
                Tags
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {tags.map((t) => <Chip key={t} size="small" label={t} variant="outlined" />)}
              </Box>
            </Box>
          )}
        </Paper>
      ) : null}

      <FormCard title="Columns" bodySx={{ p: 0 }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Data Type</TableCell>
                <TableCell>Allows Null</TableCell>
                <TableCell>Unique</TableCell>
                <TableCell>Format</TableCell>
                <TableCell>Max</TableCell>
                <TableCell>Min</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {info.columns.map((col, idx) => (
                <TableRow key={idx}>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{col.name}</TableCell>
                  <TableCell>{col.data_type}</TableCell>
                  <TableCell>{col.allow_null ? 'Yes' : 'No'}</TableCell>
                  <TableCell>{col.unique ? 'Yes' : 'No'}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{col.format || '—'}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{col.statistics?.max || '—'}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{col.statistics?.min || '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </FormCard>
    </Box>
  )
}

export default DatasetDetailPage

DatasetDetailPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Dataset">{page}</AccountLayout>
)
