import { Card, Link, AccountLayout } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi } from '@/service'
import {
  Box,
  Button,
  Chip,
  InputAdornment,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import SearchIcon from '@mui/icons-material/Search'
import { useRouter } from 'next/router'

type TypeFilter = 'ALL' | 'USER' | 'CLIENT'

function typeBadgeColor(type: string): 'primary' | 'secondary' | 'default' {
  if (type === 'USER') return 'primary'
  if (type === 'CLIENT') return 'secondary'
  return 'default'
}

function SubjectAdminPage() {
  const router = useRouter()
  const { isLoading, data, error } = useQuery(['subjectsListAdmin'], getSubjectsListUi)
  const [nameFilter, setNameFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('ALL')

  if (isLoading) return <LinearProgress />
  if (error) return <ErrorCard error={error as Error} />

  const filtered = data.filter((subject) => {
    const matchesName =
      !nameFilter ||
      (subject.subject_name ?? '').toLowerCase().includes(nameFilter.toLowerCase())
    const matchesType = typeFilter === 'ALL' || subject.type === typeFilter
    return matchesName && matchesType
  })

  return (
    <Card>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h2">User Admin</Typography>
        <Button variant="contained" color="primary" href="/subject/create/">
          + Create user
        </Button>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search by name"
          value={nameFilter}
          onChange={(e) => setNameFilter(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            )
          }}
          sx={{ minWidth: 240 }}
        />

        <ToggleButtonGroup
          value={typeFilter}
          exclusive
          size="small"
          onChange={(_e, value) => {
            if (value !== null) setTypeFilter(value as TypeFilter)
          }}
          aria-label="Type filter"
        >
          {(['ALL', 'USER', 'CLIENT'] as TypeFilter[]).map((t) => (
            <ToggleButton key={t} value={t}>
              {t}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Box>

      {filtered.length === 0 ? (
        <Typography variant="body2">No subjects found.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Subject ID</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.map((subject) => (
              <TableRow key={subject.subject_id}>
                <TableCell>{subject.subject_name}</TableCell>
                <TableCell>
                  <Chip
                    label={subject.type ?? ''}
                    color={typeBadgeColor(subject.type ?? '')}
                    size="small"
                  />
                </TableCell>
                <TableCell>{subject.subject_id}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() =>
                        router.push(
                          `/subject/modify/${subject.subject_id}?name=${encodeURIComponent(
                            subject.subject_name ?? ''
                          )}`
                        )
                      }
                    >
                      Modify
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      color="error"
                      onClick={() => router.push('/subject/delete/')}
                    >
                      Delete
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  )
}

export default SubjectAdminPage

SubjectAdminPage.getLayout = (page) => (
  <AccountLayout title="User Admin">{page}</AccountLayout>
)
