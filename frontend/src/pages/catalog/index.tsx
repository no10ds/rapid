import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getDatasetsUi } from '@/service'
import { Dataset } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ReactNode, useState, useMemo } from 'react'
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TextField,
  Select,
  MenuItem,
  Chip,
  Pagination,
  Typography,
  LinearProgress,
  InputAdornment
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'

const PAGE_SIZE = 20

function layerColor(layer: string): 'info' | 'success' | 'warning' | 'default' {
  switch (layer?.toLowerCase()) {
    case 'raw': return 'info'
    case 'curated': return 'success'
    case 'processed': return 'warning'
    default: return 'default'
  }
}

function formatDate(raw: string | undefined): string {
  if (!raw) return '—'
  const d = new Date(raw)
  if (isNaN(d.getTime())) return raw
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

type SortCol = 'domain' | 'dataset' | 'last_updated' | 'last_uploaded_by'

function CatalogPage() {
  const router = useRouter()

  const initialSearch = typeof router.query.q === 'string' ? router.query.q : ''

  const [layerFilter, setLayerFilter] = useState('All')
  const [domainFilter, setDomainFilter] = useState('All')
  const [search, setSearch] = useState(initialSearch)
  const [page, setPage] = useState(1)
  const [sortCol, setSortCol] = useState<SortCol | null>(null)
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

  function handleSort(col: SortCol) {
    if (sortCol === col) {
      setSortDir((d) => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortCol(col)
      setSortDir(col === 'domain' || col === 'dataset' ? 'asc' : 'desc')
    }
    setPage(1)
  }

  if (error) return <ErrorCard error={error as Error} />

  return (
    <Paper variant="outlined">
      {/* Toolbar */}
      <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
          <Select
            size="small"
            value={domainFilter}
            onChange={(e) => { setDomainFilter(e.target.value); setPage(1) }}
            sx={{ minWidth: 140, fontSize: 13 }}
          >
            {domains.map((d) => <MenuItem key={d} value={d} sx={{ fontSize: 13 }}>{d === 'All' ? 'All Domains' : d}</MenuItem>)}
          </Select>
          <TextField
            size="small"
            placeholder="Search by dataset name…"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            sx={{ flex: 1, minWidth: 200 }}
            InputProps={{
              startAdornment: <InputAdornment position="start"><SearchIcon sx={{ fontSize: 18, color: 'text.disabled' }} /></InputAdornment>,
              sx: { fontSize: 13 }
            }}
          />
        </Box>
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          {layers.map((f) => (
            <Chip
              key={f}
              label={f}
              size="small"
              variant={layerFilter === f ? 'filled' : 'outlined'}
              color={layerFilter === f ? 'primary' : 'default'}
              onClick={() => { setLayerFilter(f); setPage(1) }}
            />
          ))}
        </Box>
      </Box>

      {/* Table */}
      <TableContainer>
        <Table sx={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: '15%' }}>
                <TableSortLabel active={sortCol === 'domain'} direction={sortCol === 'domain' ? sortDir : 'asc'} onClick={() => handleSort('domain')}>
                  Domain
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ width: '22%' }}>
                <TableSortLabel active={sortCol === 'dataset'} direction={sortCol === 'dataset' ? sortDir : 'asc'} onClick={() => handleSort('dataset')}>
                  Dataset
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ width: '8%' }}>Version</TableCell>
              <TableCell sx={{ width: '12%' }}>Layer</TableCell>
              <TableCell sx={{ width: '22%' }}>
                <TableSortLabel active={sortCol === 'last_updated'} direction={sortCol === 'last_updated' ? sortDir : 'desc'} onClick={() => handleSort('last_updated')}>
                  Last Updated
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ width: '21%' }}>
                <TableSortLabel active={sortCol === 'last_uploaded_by'} direction={sortCol === 'last_uploaded_by' ? sortDir : 'desc'} onClick={() => handleSort('last_uploaded_by')}>
                  Updated By
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {!datasetsList ? (
              <TableRow>
                <TableCell colSpan={6} sx={{ textAlign: 'center', py: 5 }}>
                  <LinearProgress color="primary" role="progressbar" />
                </TableCell>
              </TableRow>
            ) : pageItems.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} sx={{ textAlign: 'center', py: 5, color: 'text.disabled', fontSize: 13 }}>
                  {filtered.length === 0 && !search && domainFilter === 'All' && layerFilter === 'All'
                    ? 'No datasets available.'
                    : 'No datasets match the current filters.'}
                </TableCell>
              </TableRow>
            ) : (
              pageItems.map((d) => (
                <TableRow
                  key={`${d.layer}/${d.domain}/${d.dataset}`}
                  hover
                  onClick={() => router.push(`/dataset/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{d.domain}</TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>
                    <Link
                      href={`/dataset/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`}
                      style={{ color: '#ec4899', textDecoration: 'none' }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {d.dataset}
                    </Link>
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{d.version}</TableCell>
                  <TableCell>
                    <Chip label={d.layer} size="small" color={layerColor(d.layer)} variant="outlined" />
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{formatDate(d.last_updated)}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{d.last_uploaded_by ?? '—'}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: 2, py: 1.5, borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="body2" sx={{ fontSize: 12 }}>
          {!datasetsList
            ? 'Loading...'
            : filtered.length === 0
              ? 'No datasets'
              : `Showing ${(safePage - 1) * PAGE_SIZE + 1}–${Math.min(safePage * PAGE_SIZE, filtered.length)} of ${filtered.length} dataset${filtered.length !== 1 ? 's' : ''}`}
        </Typography>
        {totalPages > 1 && (
          <Pagination
            count={totalPages}
            page={safePage}
            onChange={(_, p) => setPage(p)}
            size="small"
            color="primary"
          />
        )}
      </Box>
    </Paper>
  )
}

export default CatalogPage

CatalogPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Data Catalog">{page}</AccountLayout>
)
