import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getAllJobs } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { ReactNode, useState, useMemo } from 'react'

function getStatusBadge(status: string) {
  if (status === 'SUCCESS')
    return <span className="badge ok"><span className="bdot" />Success</span>
  if (status === 'IN PROGRESS')
    return <span className="badge pnd"><span className="bdot" />In Progress</span>
  if (status === 'FAILED')
    return <span className="badge err"><span className="bdot" />Failed</span>
  return <span className="badge">{status}</span>
}

function formatTs(ts: number | string | undefined): string | null {
  if (!ts) return null
  const n = typeof ts === 'string' ? parseInt(ts, 10) : ts
  if (!n || isNaN(n)) return null
  return new Date(n * 1000).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

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

  if (isLoading) return <div className="rapid-loading-bar" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  return (
    <div data-testid="tasks-content">
      <div className="tbl-wrap">
        <div className="tbl-toolbar" style={{ gap: '12px', flexWrap: 'wrap' }}>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', flex: 1 }}>
            View all tracked asynchronous processing jobs.
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            {typeFilters.map((f) => (
              <button
                key={f}
                className={`fchip${typeFilter === f ? ' on' : ''}`}
                onClick={() => setTypeFilter(f)}
                type="button"
              >
                {f}
              </button>
            ))}
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Type</th>
              <th>Layer</th>
              <th>Domain</th>
              <th>Dataset</th>
              <th>Version</th>
              <th>Status</th>
              <th>Step</th>
              {hasCreatedAt && <th>Created At</th>}
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td
                  colSpan={hasCreatedAt ? 10 : 9}
                  style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-tertiary)', fontSize: '13px' }}
                >
                  No {typeFilter !== 'All' ? typeFilter.toLowerCase() : ''} jobs found.
                </td>
              </tr>
            ) : (
              filtered.map((job, idx) => {
                const createdAtStr = formatTs(job.createdat as number | string | undefined)
                return (
                  <tr key={idx}>
                    <td className="mn">
                      <a href={`tasks/${job.job_id}`} style={{ color: 'var(--pink)', textDecoration: 'none' }}>
                        {job.job_id}
                      </a>
                    </td>
                    <td>{job.type}</td>
                    <td>{job.layer}</td>
                    <td>{job.domain}</td>
                    <td style={{ fontWeight: 500 }}>{job.dataset}</td>
                    <td className="mn">{job.version}</td>
                    <td>{getStatusBadge(job.status as string)}</td>
                    <td className="mn">{job.step}</td>
                    {hasCreatedAt && (
                      <td className="mn">{createdAtStr ?? <span style={{ color: 'var(--text-tertiary)' }}>—</span>}</td>
                    )}
                    <td>
                      {job.status === 'FAILED' && (
                        <a href={`tasks/${job.job_id}`} className="act-btn act-btn-del">
                          Failure Details
                        </a>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
        <div className="pager">
          <div className="pg-info">
            {filtered.length} job{filtered.length !== 1 ? 's' : ''}
            {typeFilter !== 'All' ? ` (${typeFilter.toLowerCase()})` : ''}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatusPage

StatusPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Jobs">{page}</AccountLayout>
)
