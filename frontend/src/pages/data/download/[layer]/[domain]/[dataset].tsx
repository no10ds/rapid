import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getDatasetInfo, queryDataset } from '@/service'
import { DataFormats } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'
import Link from 'next/link'

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

  if (isDatasetInfoLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (datasetInfoError) {
    return <ErrorCard error={datasetInfoError as Error} />
  }

  const addListValueToQuery = (
    queryBodyData: Record<string, unknown>,
    key: string,
    value: string
  ) => {
    if (value) {
      queryBodyData[key] = value.split(',')
    }
  }

  const addStringValueToQuery = (
    queryBodyData: Record<string, unknown>,
    key: string,
    value: string
  ) => {
    if (value) {
      queryBodyData[key] = value
    }
  }

  const createQueryBodyData = () => {
    const queryBodyData: Record<string, unknown> = {}
    addListValueToQuery(queryBodyData, 'select_columns', queryBody.select_columns)
    addStringValueToQuery(queryBodyData, 'filter', queryBody.filter)
    addListValueToQuery(queryBodyData, 'group_by_columns', queryBody.group_by_columns)
    addStringValueToQuery(
      queryBodyData,
      'aggregation_conditions',
      queryBody.aggregation_conditions
    )
    addStringValueToQuery(queryBodyData, 'limit', queryBody.limit)
    return queryBodyData
  }

  const overviewRows: [string, string][] = [
    ['Domain', domain as string],
    ['Dataset', dataset as string],
    ['Description', datasetInfoData.metadata.description],
    ['Version', version as string],
    ['Last updated', datasetInfoData.metadata.last_updated],
    ['Last uploaded by', datasetInfoData.metadata.last_uploaded_by || 'Unknown'],
    ['Number of rows', datasetInfoData.metadata.number_of_rows?.toString()],
    ['Number of columns', datasetInfoData.metadata.number_of_columns?.toString()]
  ]

  return (
    <div className="form-wrap-wide">
      {/* Card 1 — Dataset overview */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Dataset overview</div>
        </div>
        <div className="form-card-body" style={{ padding: 0 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              {overviewRows.map(([k, v]) => (
                <tr key={k} style={{ borderBottom: '1px solid #f9fafb' }}>
                  <td
                    style={{
                      width: '200px',
                      padding: '10px 16px',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: 'var(--text-tertiary)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em'
                    }}
                  >
                    {k}
                  </td>
                  <td className="mn" style={{ padding: '10px 16px' }}>
                    {v}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Card 2 — Columns */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">2</div>
          <div className="form-card-title">Columns</div>
        </div>
        <div className="form-card-body" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Data Type</th>
                <th>Allows Null</th>
                <th>Is Unique</th>
                <th>Max</th>
                <th>Min</th>
              </tr>
            </thead>
            <tbody>
              {datasetInfoData.columns.map((column, idx) => (
                <tr key={idx}>
                  <td className="mn">{column.name}</td>
                  <td>{column.data_type}</td>
                  <td>{column.allow_null ? 'True' : 'False'}</td>
                  <td>{column.unique ? 'True' : 'False'}</td>
                  <td className="mn">{column.statistics ? column.statistics.max : '—'}</td>
                  <td className="mn">{column.statistics ? column.statistics.min : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Card 3 — Query (optional) */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">3</div>
          <div className="form-card-title">
            Query
            <span
              style={{
                fontWeight: 400,
                color: 'var(--text-tertiary)',
                fontSize: '11px',
                marginLeft: '6px'
              }}
            >
              (optional)
            </span>
          </div>
        </div>
        <div className="form-card-body">
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
            {
              key: 'group_by_columns',
              label: 'Group by Columns',
              placeholder: 'column1, column3'
            },
            {
              key: 'aggregation_conditions',
              label: 'Aggregation Conditions',
              placeholder: 'avg(column2) <= 15'
            },
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
      </div>

      {/* Card 4 — Format & Download */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">4</div>
          <div className="form-card-title">Output format</div>
        </div>
        <div className="form-card-body">
          <div style={{ display: 'flex', gap: '8px' }}>
            {(['csv', 'json'] as DataFormats[]).map((fmt) => (
              <button
                key={fmt}
                type="button"
                onClick={() => setDataFormat(fmt)}
                className={`fchip${dataFormat === fmt ? ' on' : ''}`}
                style={{
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  fontSize: '11px'
                }}
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
        <div className="form-actions">
          <button
            className="btn-primary"
            type="button"
            disabled={isLoading}
            onClick={() =>
              mutate({
                path: `${layer}/${domain}/${dataset}/query?version=${version}`,
                dataFormat,
                data: createQueryBodyData()
              })
            }
          >
            {isLoading ? 'Downloading…' : 'Download'}
          </button>
          <Link href="/data/download" className="btn-secondary">
            Back
          </Link>
        </div>
      </div>

      {noContentReturn && (
        <div className="warn-box">
          No data returned for this query. Please ensure that data has been uploaded and the
          query is not too restrictive.
        </div>
      )}
      {error && <div className="warn-box">{error?.message}</div>}
    </div>
  )
}

export default DownloadDataset

DownloadDataset.getLayout = (page: ReactNode) => (
  <AccountLayout title="Download">{page}</AccountLayout>
)
