import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import UploadProgress from '@/components/UploadProgress/UploadProgress'
import { getDatasetInfo, getMethods, queryDataset, uploadDataset } from '@/service'
import { DataFormats, UploadDatasetResponse, UploadDatasetResponseDetails } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'

type ActiveTab = 'download' | 'upload' | null

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
    return <div className="rapid-loading-bar" role="progressbar" />
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

  return (
    <div className="form-wrap-wide">
      {/* Actions bar */}
      <div className="detail-actions">
        {methods?.can_download && (
          <button
            type="button"
            className={activeTab === 'download' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setActiveTab(activeTab === 'download' ? null : 'download')}
          >
            Download
          </button>
        )}
        {methods?.can_upload && (
          <button
            type="button"
            className={activeTab === 'upload' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setActiveTab(activeTab === 'upload' ? null : 'upload')}
          >
            Upload
          </button>
        )}
        {methods?.can_create_schema && (
          <button
            type="button"
            className="btn-secondary"
            onClick={() => router.push(
              `/schema/edit/${layer}/${domain}/${dataset}?version=${version}`
            )}
          >
            Edit Dataset
          </button>
        )}
        {methods?.can_create_schema && (
          <button
            type="button"
            className="act-btn act-btn-del"
            onClick={() => router.push({
              pathname: '/data/delete',
              query: { layer: layer as string, domain: domain as string, dataset: dataset as string }
            })}
          >
            Delete
          </button>
        )}
      </div>

      {/* Download panel */}
      {activeTab === 'download' && methods?.can_download && (
        <div className="form-card">
          <div className="form-card-hd">
            <div className="form-card-title">Download</div>
          </div>
          <div className="form-card-body">
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)', alignSelf: 'center', marginRight: '8px' }}>Format:</span>
              {(['csv', 'json'] as DataFormats[]).map((fmt) => (
                <button
                  key={fmt}
                  type="button"
                  onClick={() => setDataFormat(fmt)}
                  className={`fchip${dataFormat === fmt ? ' on' : ''}`}
                  style={{ textTransform: 'uppercase', letterSpacing: '0.06em', fontSize: '11px' }}
                >
                  {fmt.toUpperCase()}
                </button>
              ))}
            </div>

            <button
              type="button"
              className="detail-query-toggle"
              onClick={() => setShowQuery(!showQuery)}
            >
              {showQuery ? 'Hide query options' : 'Show query options (optional)'}
            </button>

            {showQuery && (
              <div style={{ marginTop: '16px' }}>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  For further information on writing queries consult the{' '}
                  <a
                    href="https://rapid.readthedocs.io/en/latest/api/query/"
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: 'var(--pink)', textDecoration: 'none' }}
                  >
                    query writing guide
                  </a>
                </p>
                {[
                  { key: 'select_columns', label: 'Select Columns', placeholder: 'column1, avg(column2)' },
                  { key: 'filter', label: 'Filter', placeholder: 'column >= 10' },
                  { key: 'group_by_columns', label: 'Group by Columns', placeholder: 'column1, column3' },
                  { key: 'aggregation_conditions', label: 'Aggregation Conditions', placeholder: 'avg(column2) <= 15' },
                  { key: 'limit', label: 'Row Limit', placeholder: '30' }
                ].map(({ key, label, placeholder }) => (
                  <div className="field-row" key={key}>
                    <label className="f-lbl">{label}</label>
                    <input
                      className="f-sel"
                      placeholder={placeholder}
                      value={queryBody[key as keyof typeof queryBody]}
                      onChange={(e) => setQueryBody({ ...queryBody, [key]: e.target.value })}
                    />
                  </div>
                ))}
              </div>
            )}

            <div className="form-actions" style={{ marginTop: '16px' }}>
              <button
                className="btn-primary"
                type="button"
                disabled={isDownloading}
                onClick={() =>
                  mutate({
                    path: `${layer}/${domain}/${dataset}/query?version=${version}`,
                    dataFormat,
                    data: createQueryBodyData()
                  })
                }
              >
                {isDownloading ? 'Downloading...' : 'Download'}
              </button>
            </div>

            {noContentReturn && (
              <div className="warn-box" style={{ marginTop: '12px' }}>
                No data returned for this query. Please ensure that data has been uploaded and the
                query is not too restrictive.
              </div>
            )}
            {downloadError && <div className="warn-box" style={{ marginTop: '12px' }}>{downloadError?.message}</div>}
          </div>
        </div>
      )}

      {/* Upload panel */}
      {activeTab === 'upload' && methods?.can_upload && (
        <div className="form-card">
          <div className="form-card-hd">
            <div className="form-card-title">Upload</div>
          </div>
          <div className="form-card-body">
            {!uploadDisable && (
              <label className="upload-zone" htmlFor="detail-upload-file">
                <div className="upload-ico">↑</div>
                <div className="upload-text">Drag & drop your CSV file here</div>
                <div className="upload-sub">or click to browse — CSV only, max 100 MB</div>
                {uploadFile && (
                  <div style={{ fontSize: '12px', color: 'var(--pink)', fontWeight: 500 }}>
                    {uploadFile.name}
                  </div>
                )}
              </label>
            )}
            <input
              id="detail-upload-file"
              type="file"
              style={{ display: 'none' }}
              onChange={(e) => setUploadFile(e.target.files?.[0])}
            />

            {uploadDetails && (
              <div style={{ marginTop: '16px' }}>
                <UploadProgress
                  uploadSuccessDetails={uploadDetails}
                  setDisableUpload={setUploadDisable}
                />
              </div>
            )}

            {uploadError && (
              <div className="warn-box" style={{ marginTop: '12px' }}>
                {uploadError.message}
              </div>
            )}
          </div>
          <div className="form-actions">
            <button
              className="btn-primary"
              type="button"
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
              {isUploading ? 'Uploading...' : 'Upload dataset'}
            </button>
          </div>
        </div>
      )}

      {/* Dataset header */}
      <div className="ds-header">
        <div className="ds-header-top">
          <h1 className="ds-title">{dataset}</h1>
          <span className={`badge ${({'raw':'raw','curated':'cur','processed':'proc'} as Record<string,string>)[(layer as string)?.toLowerCase()] || ''}`}>
            {layer}
          </span>
          <span className="ds-sensitivity">{meta.sensitivity}</span>
        </div>
        <div className="ds-breadcrumb">{layer} / {domain} / {dataset}</div>
        {meta.description && <p className="ds-description">{meta.description}</p>}
      </div>

      {/* Key stats */}
      <div className="ds-stats">
        <div className="ds-stat">
          <div className="ds-stat-value">{meta.number_of_rows?.toLocaleString() ?? '—'}</div>
          <div className="ds-stat-label">Rows</div>
        </div>
        <div className="ds-stat">
          <div className="ds-stat-value">{meta.number_of_columns?.toLocaleString() ?? '—'}</div>
          <div className="ds-stat-label">Columns</div>
        </div>
        <div className="ds-stat">
          <div className="ds-stat-value">{version}</div>
          <div className="ds-stat-label">Version</div>
        </div>
        <div className="ds-stat">
          <div className="ds-stat-value">{meta.last_updated || '—'}</div>
          <div className="ds-stat-label">Last Updated</div>
        </div>
        <div className="ds-stat">
          <div className="ds-stat-value">{meta.last_uploaded_by || '—'}</div>
          <div className="ds-stat-label">Uploaded By</div>
        </div>
      </div>

      {/* Secondary details */}
      {(meta.owners?.length || tags.length || meta.update_behaviour) && (
        <div className="ds-details">
          {meta.update_behaviour && (
            <div className="ds-detail-item">
              <span className="ds-detail-label">Update Behaviour</span>
              <span className="ds-detail-value">{meta.update_behaviour}</span>
            </div>
          )}
          {meta.owners && meta.owners.length > 0 && (
            <div className="ds-detail-item">
              <span className="ds-detail-label">Owners</span>
              <span className="ds-detail-value">
                {meta.owners.map((o) => `${o.name} (${o.email})`).join(', ')}
              </span>
            </div>
          )}
          {tags.length > 0 && (
            <div className="ds-detail-item">
              <span className="ds-detail-label">Tags</span>
              <span className="ds-detail-value">
                {tags.map((t) => (
                  <span key={t} className="ds-tag">{t}</span>
                ))}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Columns */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-title">Columns</div>
        </div>
        <div className="form-card-body" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Data Type</th>
                <th>Allows Null</th>
                <th>Unique</th>
                <th>Format</th>
                <th>Max</th>
                <th>Min</th>
              </tr>
            </thead>
            <tbody>
              {info.columns.map((col, idx) => (
                <tr key={idx}>
                  <td className="mn">{col.name}</td>
                  <td>{col.data_type}</td>
                  <td>{col.allow_null ? 'Yes' : 'No'}</td>
                  <td>{col.unique ? 'Yes' : 'No'}</td>
                  <td className="mn">{col.format || '—'}</td>
                  <td className="mn">{col.statistics?.max || '—'}</td>
                  <td className="mn">{col.statistics?.min || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default DatasetDetailPage

DatasetDetailPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Dataset">{page}</AccountLayout>
)
