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
    <div className="hp-wrap" data-testid="intro">
      <div className="hp-hero">
        <div className="hp-hero-glow" />
        <div className="hp-hero-wave" />
        <div className="hp-hero-wave-2" />
        <div className="hp-hero-inner">
          <h1 className="hp-hero-title">Welcome to rAPId</h1>
          <p className="hp-hero-sub">
            Your centralised platform for sharing, discovering and managing datasets.
          </p>
          <div className="hp-hero-ctas">
            <Link href="/catalog" className="hp-hero-cta">
              Explore the Catalog
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M7 17L17 7M17 7H7M17 7V17" />
              </svg>
            </Link>
          </div>
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
      </div>

      {(data?.can_upload || data?.can_download) && (
        <span data-testid="data-management" />
      )}
      {data?.can_create_schema && (
        <span data-testid="schema-management" />
      )}
      {data?.can_manage_users && (
        <span data-testid="user-management" />
      )}
    </div>
  )
}

export default AccountIndexPage

AccountIndexPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Dashboard">{page}</AccountLayout>
)
