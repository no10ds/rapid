import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getDatasetsUi } from '@/service'
import { Dataset } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
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
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [page, setPage] = useState(1)
  const [bulkDownloading, setBulkDownloading] = useState(false)

  const { isLoading, data: datasetsList, error } = useQuery(
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

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const safePage = Math.min(page, totalPages)
  const pageItems = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE)

  const datasetKey = (d: Dataset) => `${d.layer}/${d.domain}/${d.dataset}`

  const allPageSelected = pageItems.length > 0 && pageItems.every((d) => selected.has(datasetKey(d)))

  function toggleSelectAll() {
    if (allPageSelected) {
      setSelected((prev) => {
        const next = new Set(prev)
        pageItems.forEach((d) => next.delete(datasetKey(d)))
        return next
      })
    } else {
      setSelected((prev) => {
        const next = new Set(prev)
        pageItems.forEach((d) => next.add(datasetKey(d)))
        return next
      })
    }
  }

  function toggleRow(d: Dataset) {
    const k = datasetKey(d)
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(k)) next.delete(k)
      else next.add(k)
      return next
    })
  }

  function handleSingleDownload(d: Dataset) {
    router.push(`/data/download/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`)
  }

  async function handleBulkDownload() {
    const items = (datasetsList as Dataset[]).filter((d) => selected.has(datasetKey(d)))
    if (items.length === 1) {
      handleSingleDownload(items[0])
      return
    }
    setBulkDownloading(true)
    for (const d of items) {
      await router.prefetch(`/data/download/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`)
    }
    // Navigate to each in sequence — for multiple just go to the first and let user know
    // Per requirements: download them all one by one without query (non-interactive batch)
    // Since we can't trigger multiple browser downloads from navigation, we go to the first
    // and inform. In practice the bulk flow is: navigate to each download page sequentially.
    // Here we navigate to them in order.
    for (const d of items) {
      router.push(`/data/download/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`)
    }
    setBulkDownloading(false)
  }

  if (isLoading) return <div className="rapid-loading-bar" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  return (
    <div>
      {/* Bulk action bar */}
      {selected.size > 0 && (
        <div className="cat-bulk-bar">
          <span className="cat-bulk-count">{selected.size} dataset{selected.size !== 1 ? 's' : ''} selected</span>
          <button
            type="button"
            className="btn-primary"
            style={{ height: 28, fontSize: 11 }}
            onClick={handleBulkDownload}
            disabled={bulkDownloading}
          >
            ↓ Download selected
          </button>
          <span
            className="cat-bulk-clear"
            onClick={() => setSelected(new Set())}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && setSelected(new Set())}
          >
            ✕ Clear
          </span>
        </div>
      )}

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
              <th style={{ width: 36, padding: '10px 8px 10px 16px' }}>
                <input
                  type="checkbox"
                  title="Select all on page"
                  checked={allPageSelected}
                  onChange={toggleSelectAll}
                  style={{ cursor: 'pointer', width: 14, height: 14, accentColor: 'var(--pink)' }}
                />
              </th>
              <th style={{ width: '13%' }}>Domain</th>
              <th style={{ width: '18%' }}>Dataset</th>
              <th style={{ width: '7%' }}>Version</th>
              <th style={{ width: '9%' }}>Layer</th>
              <th style={{ width: '16%' }}>Last Updated</th>
              <th style={{ width: '14%' }}>Updated By</th>
              <th style={{ width: '17%' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pageItems.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-tertiary)', fontSize: '13px' }}>
                  {filtered.length === 0 && !search && domainFilter === 'All' && layerFilter === 'All'
                    ? 'No datasets available.'
                    : 'No datasets match the current filters.'}
                </td>
              </tr>
            ) : (
              pageItems.map((d) => {
                const k = datasetKey(d)
                const isSelected = selected.has(k)
                return (
                  <tr
                    key={k}
                    style={isSelected ? { background: 'rgba(236,72,153,.04)' } : undefined}
                  >
                    <td style={{ padding: '8px 8px 8px 16px' }}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleRow(d)}
                        style={{ cursor: 'pointer', width: 14, height: 14, accentColor: 'var(--pink)' }}
                      />
                    </td>
                    <td>{d.domain}</td>
                    <td style={{ fontWeight: 500, color: '#18181b' }}>{d.dataset}</td>
                    <td className="mn">{d.version}</td>
                    <td>{layerBadge(d.layer)}</td>
                    <td className="mn">{d.last_updated ?? '—'}</td>
                    <td className="mn">{d.last_uploaded_by ?? '—'}</td>
                    <td style={{ overflow: 'visible', whiteSpace: 'nowrap' }}>
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        <button
                          type="button"
                          className="act-btn"
                          style={{ color: 'var(--pink)', borderColor: 'rgba(236,72,153,.3)' }}
                          onClick={() => handleSingleDownload(d)}
                        >
                          ↓ Download
                        </button>
                        <button
                          type="button"
                          className="act-btn act-btn-del"
                          onClick={() => router.push({
                            pathname: '/data/delete',
                            query: { layer: d.layer, domain: d.domain, dataset: d.dataset }
                          })}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="pager">
          <div className="pg-info">
            {filtered.length === 0
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
