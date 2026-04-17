import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getDatasetsUi } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { ReactNode, useState } from 'react'

type LayerFilter = 'All' | 'Raw' | 'Curated' | 'Processed'

function DataAdminPage() {
  const [activeFilter, setActiveFilter] = useState<LayerFilter>('All')
  const filters: LayerFilter[] = ['All', 'Raw', 'Curated', 'Processed']

  const { isLoading, data, error } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  const allDatasets = Array.isArray(data) ? data : []

  const filtered =
    activeFilter === 'All'
      ? allDatasets
      : allDatasets.filter(
          (ds) => ds.layer?.toLowerCase() === activeFilter.toLowerCase()
        )

  const getLayerBadge = (layer: string) => {
    const l = (layer || '').toLowerCase()
    if (l === 'raw') return <span className="badge raw">Raw</span>
    if (l === 'curated') return <span className="badge cur">Curated</span>
    if (l === 'processed')
      return (
        <span className="badge" style={{ background: 'var(--green-faint)', color: '#059669' }}>
          Processed
        </span>
      )
    return <span className="badge">{layer}</span>
  }

  return (
    <div>
      <div className="tbl-wrap">
        <div className="tbl-toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flex: 1 }}>
            {filters.map((f) => (
              <button
                key={f}
                className={`fchip${activeFilter === f ? ' on' : ''}`}
                onClick={() => setActiveFilter(f)}
                type="button"
              >
                {f}
              </button>
            ))}
          </div>
          <span
            className="badge"
            style={{ background: 'rgba(139,92,246,.08)', color: '#7c3aed', border: '1px solid rgba(139,92,246,.18)', fontWeight: 700, letterSpacing: '0.06em' }}
          >
            Admin
          </span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Domain</th>
              <th>Layer</th>
              <th>Sensitivity</th>
              <th>Version</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length > 0 ? (
              filtered.map((ds, idx) => (
                <tr key={idx}>
                  <td className="mn" style={{ fontWeight: 500 }}>
                    {ds.dataset}
                  </td>
                  <td>{ds.domain}</td>
                  <td>{getLayerBadge(ds.layer)}</td>
                  <td>
                    {ds.sensitivity ? (
                      <span
                        className="badge"
                        style={{ background: 'var(--amber-faint)', color: '#d97706' }}
                      >
                        {ds.sensitivity}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '12px' }}>—</span>
                    )}
                  </td>
                  <td className="mn">{ds.version}</td>
                  <td>
                    <a
                      href={`/data/download/${ds.layer}/${ds.domain}/${ds.dataset}?version=${ds.version}`}
                      className="act-btn"
                    >
                      View
                    </a>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={6}
                  style={{
                    textAlign: 'center',
                    padding: '40px 20px',
                    color: 'var(--text-tertiary)',
                    fontSize: '13px'
                  }}
                >
                  No datasets found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
        <div className="pager">
          <div className="pg-info">
            {filtered.length} dataset{filtered.length !== 1 ? 's' : ''}
            {activeFilter !== 'All' ? ` in ${activeFilter}` : ''}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DataAdminPage

DataAdminPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Data Admin">{page}</AccountLayout>
)
