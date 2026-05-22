import { Dataset } from '@/service/types'
import { useRouter } from 'next/router'
import { useState, useMemo, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  TextField,
  InputAdornment,
  ClickAwayListener
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'

const MAX_SUGGESTIONS = 8

const DatasetSearchBar = ({ datasets }: { datasets: Dataset[] }) => {
  const router = useRouter()
  const [search, setSearch] = useState('')
  const [layerFilter, setLayerFilter] = useState('All')
  const [open, setOpen] = useState(false)
  const wrapRef = useRef<HTMLDivElement>(null)

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
    }).slice(0, MAX_SUGGESTIONS)
  }, [datasets, layerFilter, search])

  // Close the suggestions dropdown when the user clicks outside the wrapper.
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const goToCatalog = () => {
    const query = search.trim()
    router.push(query ? { pathname: '/catalog', query: { q: query } } : '/catalog')
  }

  return (
    <Box sx={{ maxWidth: 720, mx: 'auto', position: 'relative' }} ref={wrapRef}>
      {datasets.length > 0 && layers.length > 2 && (
        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap', mb: 2 }}>
          {layers.map((l) => (
            <Chip
              key={l}
              label={l}
              size="small"
              variant={layerFilter === l ? 'filled' : 'outlined'}
              color={layerFilter === l ? 'primary' : 'default'}
              onClick={() => { setLayerFilter(l); setOpen(true) }}
              sx={
                layerFilter !== l
                  ? { color: '#fff', borderColor: 'rgba(255,255,255,0.4)', '&:hover': { borderColor: '#fff' } }
                  : undefined
              }
            />
          ))}
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search datasets by name, domain or layer…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setOpen(true) }}
          onFocus={() => setOpen(true)}
          sx={{
            bgcolor: '#fff',
            borderRadius: 1,
            '& .MuiOutlinedInput-root': { fontSize: 14 }
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ fontSize: 18, color: 'text.disabled' }} />
              </InputAdornment>
            )
          }}
        />
        <Button variant="contained" onClick={goToCatalog} sx={{ whiteSpace: 'nowrap' }}>
          View Catalog
        </Button>
      </Box>

      {open && search.trim() && filtered.length > 0 && (
        <ClickAwayListener onClickAway={() => setOpen(false)}>
          <Paper
            elevation={4}
            sx={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              mt: 0.5,
              textAlign: 'left',
              zIndex: 10,
              maxHeight: 360,
              overflowY: 'auto'
            }}
          >
            {filtered.map((d) => {
              const key = `${d.layer}/${d.domain}/${d.dataset}`
              return (
                <Box
                  key={key}
                  onClick={() => router.push(
                    `/dataset/${d.layer}/${d.domain}/${d.dataset}?version=${d.version}`
                  )}
                  sx={{
                    cursor: 'pointer',
                    p: 1.5,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    '&:hover': { bgcolor: 'background.default' },
                    '&:last-child': { borderBottom: 0 }
                  }}
                >
                  <Typography sx={{ fontSize: 13, fontWeight: 500 }}>{d.dataset}</Typography>
                  <Typography sx={{ fontSize: 11, color: 'text.disabled' }}>
                    {d.layer} / {d.domain} {d.version ? `v${d.version}` : ''}
                  </Typography>
                </Box>
              )
            })}
          </Paper>
        </ClickAwayListener>
      )}
    </Box>
  )
}

export default DatasetSearchBar
