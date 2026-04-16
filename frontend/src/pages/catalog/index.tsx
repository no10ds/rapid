import { MetadataSearchRequest } from '@/service/types'
import AccountLayout from '@/components/Layout/AccountLayout'
import { useRouter } from 'next/router'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ReactNode, useState } from 'react'

type LayerFilter = 'All' | 'Raw' | 'Curated' | 'Processed'

function CatalogPage() {
  const router = useRouter()
  const [activeFilter, setActiveFilter] = useState<LayerFilter>('All')

  const { control, handleSubmit } = useForm<MetadataSearchRequest>({
    resolver: zodResolver(
      z.object({
        search: z.string()
      })
    )
  })

  const filters: LayerFilter[] = ['All', 'Raw', 'Curated', 'Processed']

  return (
    <div>
      <div className="tbl-wrap">
        {/* Toolbar */}
        <div className="tbl-toolbar" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '10px' }}>
          <form
            style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', width: '100%' }}
            onSubmit={handleSubmit(async (data: MetadataSearchRequest) => {
              router.push(`/catalog/${data.search}`)
            })}
          >
            <Controller
              name="search"
              control={control}
              defaultValue=""
              render={({ field }) => (
                <input
                  {...field}
                  className="search-in"
                  placeholder="Search dataset names, descriptions, columns…"
                  type="text"
                  style={{ minWidth: '260px', flex: 1 }}
                  data-testid="catalog-search-input"
                />
              )}
            />
            <button className="tb-btn" type="submit" data-testid="catalog-search-submit">
              Search
            </button>
          </form>

          {/* Layer filter chips */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
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
        </div>

        {/* Table */}
        <table>
          <thead>
            <tr>
              <th>Domain <span style={{ opacity: 0.4, fontSize: '9px' }}>↕</span></th>
              <th>Dataset <span style={{ opacity: 0.4, fontSize: '9px' }}>↕</span></th>
              <th>Version <span style={{ opacity: 0.4, fontSize: '9px' }}>↕</span></th>
              <th className="srt">Layer <span style={{ fontSize: '9px' }}>↓</span></th>
              <th>Sensitivity <span style={{ opacity: 0.4, fontSize: '9px' }}>↕</span></th>
              <th>Last Updated <span style={{ opacity: 0.4, fontSize: '9px' }}>↕</span></th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={7} style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-tertiary)', fontSize: '13px' }}>
                Use the search above to find datasets in the catalog.
              </td>
            </tr>
          </tbody>
        </table>

        {/* Pagination placeholder */}
        <div className="pager">
          <div className="pg-info">Search for datasets above</div>
        </div>
      </div>
    </div>
  )
}

export default CatalogPage

CatalogPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Data Catalog">
    {page}
  </AccountLayout>
)
