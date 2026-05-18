import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getDatasetsUi } from '@/service'
import { Dataset } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ReactNode, useState, useMemo } from 'react'

const PAGE_SIZE = 20

const LAYER_BADGE_CLASS: Record<string, string> = {
  raw: 'raw',
  curated: 'cur',
  processed: 'proc'
}

function layerBadge(layer: string) {
  const mod = LAYER_BADGE_CLASS[layer?.toLowerCase()] ?? ''
  return <span className={`badge ${mod}`.trim()}>{layer}</span>
}

function CatalogPage() {
  const router = useRouter()

  const initialSearch = typeof router.query.q === 'string' ? router.query.q : ''

  const [layerFilter, setLayerFilter] = useState('All')
  const [domainFilter, setDomainFilter] = useState('All')
  const [search, setSearch] = useState(initialSearch)
  const [page, setPage] = useState(1)
  const [sortCol, setSortCol] = useState<'domain' | 'dataset' | 'last_updated' | 'last_uploaded_by' | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  const { data: datasetsList, error } = useQuery(
    ['datasetsList', 'READ'],
    getDatasetsUi
  )

  const layers = useMemo(() => {
    if (!datasetsList) return ['All']
    const unique = Array.from(new Set((datasetsList as Dataset[]).map((d) => d.layer).filter(Boolean))).sort()
    return ['All', ...unique]
  }, [datasetsList])

  const domains = useMemo(() => {
    if (!datasetsList) return []
    const all = Array.from(new Set((datasetsList as Dataset[]).map((d) => d.domain))).sort()
    return ['All', ...all]
  }, [datasetsList])

  const filtered = useMemo(() => {
    if (!datasetsList) return []
    return (datasetsList as Dataset[]).filter((d) => {
      if (layerFilter !== 'All' && d.layer?.toLowerCase() !== layerFilter.toLowerCase()) return false
      if (domainFilter !== 'All' && d.domain !== domainFilter) return false
      if (search.trim()) {
        const q = search.trim().toLowerCase()
        if (!d.dataset.toLowerCase().includes(q)) return false
      }
      return true
    })
  }, [datasetsList, layerFilter, domainFilter, search])

  const sorted = useMemo(() => {
    if (!sortCol) return filtered
    return [...filtered].sort((a, b) => {
      const av = (a[sortCol] ?? '').toLowerCase()
      const bv = (b[sortCol] ?? '').toLowerCase()
      if (av < bv) return sortDir === 'asc' ? -1 : 1
      if (av > bv) return sortDir === 'asc' ? 1 : -1
      return 0
    })
  }, [filtered, sortCol, sortDir])

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const safePage = Math.min(page, totalPages)
  const pageItems = sorted.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE)

  function toggleSort(col: 'domain' | 'dataset' | 'last_updated' | 'last_uploaded_by') {
    if (sortCol === col) {
      setSortDir((d) => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortCol(col)
      setSortDir(col === 'domain' || col === 'dataset' ? 'asc' : 'desc')
    }
    setPage(1)
  }

  function sortIndicator(col: 'domain' | 'dataset' | 'last_updated' | 'last_uploaded_by') {
    const isActive = sortCol === col
    const arrow = isActive ? (sortDir === 'asc' ? '↑' : '↓') : '↕'
    return <span className={`sort-icon${isActive ? ' active' : ''}`}>{arrow}</span>
  }

  if (error) return <ErrorCard error={error as Error} />

  return (
    <div>
      <div className="tbl-wrap">
        {/* Toolbar */}
        <div className="tbl-toolbar" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', width: '100%' }}>
            {/* Domain filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span className="cat-lbl">Domain</span>
              <select
                className="cat-sel"
                value={domainFilter}
                onChange={(e) => { setDomainFilter(e.target.value); setPage(1) }}
              >
                {domains.map((d) => <option key={d}>{d}</option>)}
              </select>
            </div>
            {/* Search by dataset title */}
            <input
              className="search-in"
              placeholder="Search by dataset name…"
              type="text"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              style={{ minWidth: '220px', flex: 1 }}
            />
          </div>
          {/* Layer filter chips */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            {layers.map((f) => (
              <button
                key={f}
                className={`fchip${layerFilter === f ? ' on' : ''}`}
                onClick={() => { setLayerFilter(f); setPage(1) }}
                type="button"
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <table style={{ tableLayout: 'fixed' }}>
          <thead>
            <tr>
              <th style={{ width: '15%', cursor: 'pointer' }} onClick={() => toggleSort('domain')}>
                Domain{sortIndicator('domain')}
              </th>
              <th style={{ width: '22%', cursor: 'pointer' }} onClick={() => toggleSort('dataset')}>
                Dataset{sortIndicator('dataset')}
              </th>
              <th style={{ width: '8%' }}>Version</th>
              <th style={{ width: '12%' }}>Layer</th>
              <th style={{ width: '22%', cursor: 'pointer' }} onClick={() => toggleSort('last_updated')}>
                Last Updated{sortIndicator('last_updated')}
              </th>
              <th style={{ width: '21%', cursor: 'pointer' }} onClick={() => toggleSort('last_uploaded_by')}>
                Updated By{sortIndicator('last_uploaded_by')}
              </th>
            </tr>
          </thead>
          <tbody>
            {!datasetsList ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '40px 20px' }}>
                  <div className="rapid-loading-bar" role="progressbar" />
                </td>
              </tr>
            ) : pageItems.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-tertiary)', fontSize: '13px' }}>
                  {filtered.length === 0 && !search && domainFilter === 'All' && layerFilter === 'All'
                    ? 'No datasets available.'
                    : 'No datasets match the current filters.'}
                </td>
              </tr>
            ) : (
              pageItems.map((d) => (
                <tr
                  key={`${d.layer}/${d.domain}/${d.dataset}`}
                  className="cat-row-link"
                  onClick={() => router.push(`/dataset/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`)}
                >
                  <td>{d.domain}</td>
                  <td style={{ fontWeight: 500 }}>
                    <Link
                      href={`/dataset/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`}
                      style={{ color: 'var(--pink)', textDecoration: 'none' }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {d.dataset}
                    </Link>
                  </td>
                  <td className="mn">{d.version}</td>
                  <td>{layerBadge(d.layer)}</td>
                  <td className="mn">{d.last_updated ?? '—'}</td>
                  <td className="mn">{d.last_uploaded_by ?? '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="pager">
          <div className="pg-info">
            {!datasetsList
              ? 'Loading...'
              : filtered.length === 0
                ? 'No datasets'
                : `Showing ${(safePage - 1) * PAGE_SIZE + 1}–${Math.min(safePage * PAGE_SIZE, filtered.length)} of ${filtered.length} dataset${filtered.length !== 1 ? 's' : ''}`}
          </div>
          {totalPages > 1 && (
            <>
              <button
                type="button"
                className="pg-btn"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={safePage === 1}
              >
                ‹
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((n) => (
                <button
                  key={n}
                  type="button"
                  className={`pg-btn${n === safePage ? ' on' : ''}`}
                  onClick={() => setPage(n)}
                >
                  {n}
                </button>
              ))}
              <button
                type="button"
                className="pg-btn"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={safePage === totalPages}
              >
                ›
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default CatalogPage

CatalogPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Data Catalog">{page}</AccountLayout>
)
