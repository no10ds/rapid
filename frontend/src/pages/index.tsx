import AccountLayout from '@/components/Layout/AccountLayout'
import { useQuery } from '@tanstack/react-query'
import { getMethods, getDatasetsUi } from '@/service'
import { Dataset } from '@/service/types'
import { ReactNode, useState, useMemo, useRef, useEffect } from 'react'
import { useRouter } from 'next/router'

function AccountIndexPage() {
  const router = useRouter()
  const [search, setSearch] = useState('')
  const [layerFilter, setLayerFilter] = useState('All')
  const [open, setOpen] = useState(false)
  const wrapRef = useRef<HTMLDivElement>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['methods'],
    queryFn: getMethods,
    keepPreviousData: false,
    cacheTime: 0,
    refetchInterval: 0
  })

  const canRead = data?.can_download || data?.can_search_catalog
  const canWrite = data?.can_upload

  const { data: readDatasets } = useQuery(
    ['datasetsList', 'READ'],
    getDatasetsUi,
    { enabled: !!canRead }
  )

  const { data: writeDatasets } = useQuery(
    ['datasetsList', 'WRITE'],
    getDatasetsUi,
    { enabled: !!canWrite && !canRead }
  )

  const datasets: Dataset[] = (readDatasets ?? writeDatasets ?? []) as Dataset[]

  const layers = useMemo(() => {
    const unique = Array.from(new Set(datasets.map((d) => d.layer).filter(Boolean))).sort()
    return ['All', ...unique]
  }, [datasets])

  const filtered = useMemo(() => {
    return datasets.filter((d) => {
      if (layerFilter !== 'All' && d.layer?.toLowerCase() !== layerFilter.toLowerCase()) return false
      if (search.trim()) {
        const q = search.trim().toLowerCase()
        const haystack = `${d.layer} ${d.domain} ${d.dataset}`.toLowerCase()
        if (!haystack.includes(q)) return false
      }
      return true
    }).slice(0, 8)
  }, [datasets, layerFilter, search])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

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

          <div className="hp-search-wrap" ref={wrapRef}>
            {/* Layer filter chips */}
            {datasets.length > 0 && layers.length > 2 && (
              <div className="hp-filter-chips">
                {layers.map((l) => (
                  <button
                    key={l}
                    type="button"
                    className={`hp-chip${layerFilter === l ? ' on' : ''}`}
                    onClick={() => { setLayerFilter(l); setOpen(true) }}
                  >
                    {l}
                  </button>
                ))}
              </div>
            )}

            <div className="hp-search-form">
              <input
                className="hp-search-input"
                type="text"
                placeholder="Search datasets by name, domain or layer…"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setOpen(true) }}
                onFocus={() => setOpen(true)}
              />
              <button
                className="hp-search-btn"
                type="button"
                onClick={() => {
                  if (search.trim()) {
                    router.push({ pathname: '/catalog', query: { q: search.trim() } })
                  } else {
                    router.push('/catalog')
                  }
                }}
              >
                View Catalog
              </button>
            </div>

            {/* Dropdown results */}
            {open && search.trim() && filtered.length > 0 && (
              <div className="hp-results">
                {filtered.map((d) => {
                  const key = `${d.layer}/${d.domain}/${d.dataset}`
                  return (
                    <div key={key} className="hp-result-row">
                      <div className="hp-result-info">
                        <span className="hp-result-name">{d.dataset}</span>
                        <span className="hp-result-meta">
                          {d.layer} / {d.domain} {d.version ? `v${d.version}` : ''}
                        </span>
                      </div>
                      <div className="hp-result-actions">
                        {canRead && (
                          <button
                            type="button"
                            className="hp-result-btn"
                            onClick={() => router.push(
                              `/data/download/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`
                            )}
                          >
                            Download
                          </button>
                        )}
                        {canWrite && (
                          <button
                            type="button"
                            className="hp-result-btn hp-result-btn-upload"
                            onClick={() => router.push('/data/upload')}
                          >
                            Upload
                          </button>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {open && search.trim() && filtered.length === 0 && (
              <div className="hp-results">
                <div className="hp-result-empty">No datasets match your search.</div>
              </div>
            )}
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
  <AccountLayout title="Dashboard" noPad>{page}</AccountLayout>
)
