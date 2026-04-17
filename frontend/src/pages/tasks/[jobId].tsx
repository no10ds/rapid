import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getJob } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { ReactNode } from 'react'
import Link from 'next/link'

function getStatusBadge(status: string) {
  if (status === 'SUCCESS')
    return (
      <span className="badge ok">
        <span className="bdot" />
        Success
      </span>
    )
  if (status === 'IN PROGRESS')
    return (
      <span className="badge pnd">
        <span className="bdot" />
        In Progress
      </span>
    )
  if (status === 'FAILED')
    return (
      <span className="badge err">
        <span className="bdot" />
        Failed
      </span>
    )
  return <span className="badge">{status}</span>
}

function GetJob() {
  const router = useRouter()
  const { jobId } = router.query
  const { isLoading, data, error } = useQuery(['getJob', jobId], getJob)

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  const metaRows: [string, ReactNode][] = [
    ['Job ID', <span className="mono" key="id" style={{ fontSize: '12px' }}>{data.job_id}</span>],
    ['Type', data.type as string],
    ['Status', getStatusBadge(data.status as string)],
    ['Step', data.step as string],
    ['Filename', data.filename as string],
    ['Raw Filename', data.raw_file_identifier as string],
    ['Layer', data.layer as string],
    ['Domain', data.domain as string],
    ['Dataset', data.dataset as string],
    ['Version', String(data.version)]
  ]

  return (
    <div>
      {/* Status card */}
      <div className="form-card" style={{ marginBottom: '16px' }}>
        <div className="form-card-hd">
          <div className="form-card-title">Job Detail</div>
          <div style={{ marginLeft: 'auto' }}>
            <Link href="/tasks" className="btn-secondary" style={{ textDecoration: 'none' }}>
              ← Back to Jobs
            </Link>
          </div>
        </div>
        <div className="form-card-body" style={{ padding: 0 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              {metaRows.map(([k, v]) => (
                <tr key={k as string} style={{ borderBottom: '1px solid #f9fafb' }}>
                  <td
                    style={{
                      width: '180px',
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
                  <td style={{ padding: '10px 16px', fontSize: '13px' }}>{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Errors card */}
      {data.errors && (data.errors as string[]).length > 0 && (
        <div className="form-card">
          <div className="form-card-hd form-card-hd-danger">
            <div className="form-card-num form-card-num-danger">!</div>
            <div className="form-card-title form-card-title-danger">Errors</div>
          </div>
          <div className="form-card-body">
            <div className="log-box">
              {(data.errors as string[]).map((err, i) => (
                <div key={i}>{err}</div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GetJob

GetJob.getLayout = (page: ReactNode) => (
  <AccountLayout title="Task Status">{page}</AccountLayout>
)
