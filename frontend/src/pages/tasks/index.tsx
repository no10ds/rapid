import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getAllJobs } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { ReactNode } from 'react'

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

function StatusPage() {
  const { isLoading, data, error } = useQuery(['jobs'], getAllJobs)

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  return (
    <div data-testid="tasks-content">
      <div className="tbl-wrap">
        <div className="tbl-toolbar">
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            View all tracked asynchronous processing jobs. Click a job ID for details.
          </p>
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
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.map((job, idx) => (
              <tr key={idx}>
                <td className="mn">
                  <a
                    href={`tasks/${job.job_id}`}
                    style={{ color: 'var(--pink)', textDecoration: 'none' }}
                  >
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
                <td>
                  {job.status === 'FAILED' && (
                    <a
                      href={`tasks/${job.job_id}`}
                      className="act-btn act-btn-del"
                    >
                      Failure Details
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="pager">
          <div className="pg-info">
            {data.length} job{data.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatusPage

StatusPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Task Status">{page}</AccountLayout>
)
