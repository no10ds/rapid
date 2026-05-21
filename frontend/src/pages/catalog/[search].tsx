import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getMetadataSearch } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ReactNode } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material'

type MatchField = 'columns' | 'dataset' | 'description'

function getMatchLabel(type: MatchField) {
  if (type === 'columns') return 'Column'
  if (type === 'dataset') return 'Dataset Title'
  if (type === 'description') return 'Description'
  return type
}

function getMatchColor(type: MatchField): 'error' | 'info' | 'warning' | 'default' {
  if (type === 'columns') return 'error'
  if (type === 'dataset') return 'info'
  if (type === 'description') return 'warning'
  return 'default'
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
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  if (!data.length) {
    return (
      <Paper variant="outlined" data-testid="empty-search-content" sx={{ p: 5, textAlign: 'center' }}>
        <Typography sx={{ fontSize: 15, fontWeight: 600, mb: 0.5 }}>No Results Found</Typography>
        <Typography variant="body2" sx={{ fontSize: 13, mb: 2 }}>Try a less specific query</Typography>
        <Button component={Link} href="/catalog" size="small">← Back to Catalog</Button>
      </Paper>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Button component={Link} href="/catalog" size="small">
          ← Back to Catalog
        </Button>
        <Typography variant="h3" sx={{ fontSize: 14 }}>
          Results for &ldquo;{search}&rdquo;
        </Typography>
      </Box>

      <Paper variant="outlined">
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Dataset Domain</TableCell>
                <TableCell>Dataset Title</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Match Result</TableCell>
                <TableCell>Type</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.map((item, idx) => (
                <TableRow key={idx} hover>
                  <TableCell>{item.domain}</TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>{item.dataset}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{item.version}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{item.matching_data}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      variant="outlined"
                      color={getMatchColor(item.matching_field as MatchField)}
                      label={getMatchLabel(item.matching_field as MatchField)}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Box sx={{ px: 2, py: 1.5, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="body2" sx={{ fontSize: 12 }}>
            Showing {data.length} result{data.length !== 1 ? 's' : ''} for &ldquo;{search}&rdquo;
          </Typography>
        </Box>
      </Paper>
    </Box>
  )
}

export default GetSearch

GetSearch.getLayout = (page: ReactNode) => (
  <AccountLayout title="Data Catalog">{page}</AccountLayout>
)
