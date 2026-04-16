import AccountLayout from '@/components/Layout/AccountLayout'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { getMethods } from '@/service'
import { ReactNode } from 'react'

function AccountIndexPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['methods'],
    queryFn: getMethods,
    keepPreviousData: false,
    cacheTime: 0,
    refetchInterval: 0
  })

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  return (
    <div className="hp-wrap">
      {/* ── Hero banner ──────────────────────────────────────── */}
      <div className="hp-hero">
        <div className="hp-hero-eyebrow">Data Platform</div>
        <h1 className="hp-hero-title">Welcome to rAPId</h1>
        <p className="hp-hero-sub">
          Manage, share and govern datasets across your organisation.
        </p>
        <div className="hp-hero-links">
          <a href="/api/docs" className="hp-hero-link">
            View the API docs
          </a>
          <a
            href="https://github.com/no10ds/rapid"
            className="hp-hero-link"
            target="_blank"
            rel="noreferrer"
          >
            See the source code
          </a>
          <a
            href="https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM"
            className="hp-hero-link"
            target="_blank"
            rel="noreferrer"
          >
            Contact
          </a>
        </div>
      </div>

      {/* ── Action cards ─────────────────────────────────────── */}
      <div className="hp-body">
        <div className="hp-cards" data-testid="intro">
          {/* User Management — User Admins only */}
          {data?.can_manage_users && (
            <div className="hp-card hp-card-admin" data-testid="user-management">
              <div className="hp-card-header">
                <div>
                  <div className="hp-card-title">User Management</div>
                </div>
                <div className="hp-admin-badge">User Admin only</div>
              </div>
              <p className="hp-card-desc">
                Create and modify different users and clients.
              </p>
              <div className="hp-card-actions">
                <Link href="/subject/create" className="hp-btn hp-btn-primary">
                  Create User
                </Link>
                <Link href="/subject/modify" className="hp-btn hp-btn-ghost">
                  Modify User
                </Link>
              </div>
            </div>
          )}

          {/* Data Management */}
          {(data?.can_upload || data?.can_download) && (
            <div className="hp-card hp-card-data" data-testid="data-management">
              <div className="hp-card-header">
                <div>
                  <div className="hp-card-title">Data Management</div>
                </div>
              </div>
              <p className="hp-card-desc">
                Upload and download existing data files.
              </p>
              <div className="hp-card-actions">
                {data?.can_download && (
                  <Link href="/data/download" className="hp-btn hp-btn-primary">
                    Download Data
                  </Link>
                )}
                {data?.can_upload && (
                  <Link href="/data/upload" className="hp-btn hp-btn-ghost">
                    Upload Data
                  </Link>
                )}
              </div>
            </div>
          )}

          {/* Schema Management */}
          {data?.can_create_schema && (
            <div className="hp-card hp-card-schema" data-testid="schema-management">
              <div className="hp-card-header">
                <div>
                  <div className="hp-card-title">Schema Management</div>
                </div>
              </div>
              <p className="hp-card-desc">
                Manually create new schemas from raw data.
              </p>
              <div className="hp-card-actions">
                <Link href="/schema/create" className="hp-btn hp-btn-primary">
                  Create Schema
                </Link>
              </div>
            </div>
          )}

          {/* Task Status */}
          {(data?.can_upload || data?.can_download) && (
            <div className="hp-card hp-card-data" data-testid="task-status">
              <div className="hp-card-header">
                <div>
                  <div className="hp-card-title">Task Status</div>
                </div>
              </div>
              <p className="hp-card-desc">
                View pending and complete API tasks.
              </p>
              <div className="hp-card-actions">
                <Link href="/tasks" className="hp-btn hp-btn-primary">
                  Tasks
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AccountIndexPage

AccountIndexPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Dashboard">{page}</AccountLayout>
)
