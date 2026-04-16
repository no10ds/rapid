import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getMetadataSearch } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ReactNode } from 'react'

type MatchField = 'columns' | 'dataset' | 'description'

function getMatchLabel(type: MatchField) {
  if (type === 'columns') return 'Column'
  if (type === 'dataset') return 'Dataset Title'
  if (type === 'description') return 'Description'
  return type
}

function getMatchBadgeClass(type: MatchField) {
  if (type === 'columns') return 'badge err'
  if (type === 'dataset') return 'badge raw'
  if (type === 'description') return 'badge pnd'
  return 'badge'
}

function GetSearch() {
  const router = useRouter()
  const { search } = router.query

  const { isLoading, data, error } = useQuery(
    ['metadataSearch', search],
    getMetadataSearch,
    { refetchOnMount: false }
  )

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  if (!data.length) {
    return (
      <div className="tbl-wrap" data-testid="empty-search-content">
        <div style={{ padding: '40px 24px', textAlign: 'center' }}>
          <p style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
            No Results Found
          </p>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Try a less specific query
          </p>
          <Link href="/catalog" style={{ fontSize: '12px', color: 'var(--pink)', textDecoration: 'none', marginTop: '12px', display: 'inline-block' }}>
            ← Back to Catalog
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Link href="/catalog" style={{ fontSize: '12px', color: 'var(--text-tertiary)', textDecoration: 'none' }}>
          ← Back to Catalog
        </Link>
        <h2 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
          Results for &ldquo;{search}&rdquo;
        </h2>
      </div>

      <div className="tbl-wrap">
        <table>
          <thead>
            <tr>
              <th>Dataset Domain</th>
              <th>Dataset Title</th>
              <th>Version</th>
              <th>Match Result</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr key={idx}>
                <td>{item.domain}</td>
                <td style={{ fontWeight: 500 }}>{item.dataset}</td>
                <td className="mn">{item.version}</td>
                <td className="mn">{item.matching_data}</td>
                <td>
                  <span className={getMatchBadgeClass(item.matching_field as MatchField)}>
                    {getMatchLabel(item.matching_field as MatchField)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="pager">
          <div className="pg-info">
            Showing {data.length} result{data.length !== 1 ? 's' : ''} for &ldquo;{search}&rdquo;
          </div>
        </div>
      </div>
    </div>
  )
}

export default GetSearch

GetSearch.getLayout = (page: ReactNode) => (
  <AccountLayout title="Data Catalog">{page}</AccountLayout>
)
