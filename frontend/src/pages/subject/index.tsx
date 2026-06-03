import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { sortByString } from '@/utils/sort'
import { getSubjectsListUi, getSubjectPermissions } from '@/service'
import { SubjectPermission } from '@/service/types'
import { useQuery, useQueries } from '@tanstack/react-query'
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
  Button,
  Typography,
  LinearProgress,
  InputAdornment
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import AddIcon from '@mui/icons-material/Add'

type SubjectType = 'All' | 'USER' | 'CLIENT'

type RoleFilter = 'All' | 'User Admin' | 'Data Admin' | 'Read/Write' | 'Read Only' | 'No Permissions'

const ROLE_FILTERS: RoleFilter[] = ['All', 'User Admin', 'Data Admin', 'Read/Write', 'Read Only', 'No Permissions']

// Roles in descending precedence — the first one the subject has wins.
const ROLE_PRECEDENCE = ['USER_ADMIN', 'DATA_ADMIN', 'WRITE', 'READ'] as const

function deriveRole(perms: SubjectPermission[] | undefined): RoleFilter {
  if (!perms || perms.length === 0) return 'No Permissions'
  const highest = ROLE_PRECEDENCE.find((type) => perms.some((p) => p.type === type))
  switch (highest) {
    case 'USER_ADMIN': return 'User Admin'
    case 'DATA_ADMIN': return 'Data Admin'
    case 'WRITE': return 'Read/Write'
    case 'READ': return 'Read Only'
    default: return 'No Permissions'
  }
}

function UserAdminPage() {
  const router = useRouter()
  const [typeFilter, setTypeFilter] = useState<SubjectType>('All')
  const [roleFilter, setRoleFilter] = useState<RoleFilter>('All')
  const [domainFilter, setDomainFilter] = useState('All')
  const [search, setSearch] = useState('')
  const [sortCol, setSortCol] = useState<'subject_name' | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const { isLoading, data, error } = useQuery(['subjectsList'], getSubjectsListUi, {
    staleTime: Infinity,
    keepPreviousData: true
  })

  const permissionQueries = useQueries({
    queries: (data ?? []).map((s) => ({
      queryKey: ['subjectPermissions', s.subject_id],
      queryFn: getSubjectPermissions,
      enabled: !!s.subject_id,
      staleTime: Infinity,
      keepPreviousData: true
    }))
  })

  const permsBySubjectId = useMemo(() => {
    if (!data) return {}
    return Object.fromEntries(
      data.map((s, i) => [s.subject_id, permissionQueries[i]?.data as SubjectPermission[] | undefined])
    )
  }, [data, permissionQueries])

  const allDomains = useMemo(() => {
    const domains = new Set<string>()
    Object.values(permsBySubjectId).forEach((perms) => {
      perms?.forEach((p) => { if (p.domain) domains.add(p.domain) })
    })
    return ['All', ...Array.from(domains).sort()]
  }, [permsBySubjectId])

  const filtered = useMemo(() => {
    if (!data) return []
    const query = search.trim().toLowerCase()

    const matchesType = (s: typeof data[number]) =>
      typeFilter === 'All' || s.type === typeFilter

    const matchesSearch = (s: typeof data[number]) =>
      !query || String(s.subject_name ?? '').toLowerCase().includes(query)

    const matchesRole = (perms: SubjectPermission[] | undefined) =>
      roleFilter === 'All' || deriveRole(perms) === roleFilter

    const matchesDomain = (perms: SubjectPermission[] | undefined) =>
      domainFilter === 'All' || !!perms?.some((p) => p.domain === domainFilter)

    return data.filter((s) => {
      const perms = permsBySubjectId[s.subject_id as string]
      return matchesType(s) && matchesSearch(s) && matchesRole(perms) && matchesDomain(perms)
    })
  }, [data, typeFilter, roleFilter, domainFilter, search, permsBySubjectId])

  const sorted = useMemo(
    () => sortByString(filtered, sortCol, sortDir),
    [filtered, sortCol, sortDir]
  )

  function handleSort() {
    if (sortCol === 'subject_name') {
      setSortDir((d) => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortCol('subject_name')
      setSortDir('asc')
    }
  }

  if (isLoading) return <LinearProgress color="primary" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  const typeFilters: SubjectType[] = ['All', 'USER', 'CLIENT']

  return (
    <Paper variant="outlined">
      {/* Toolbar */}
      <Box sx={{ px: '18px', py: '14px', display: 'flex', flexDirection: 'column', gap: '14px', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <TextField
            size="small"
            placeholder="Search by name…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flex: 1, minWidth: 200 }}
            InputProps={{
              startAdornment: <InputAdornment position="start"><SearchIcon sx={{ fontSize: 18, color: 'text.disabled' }} /></InputAdornment>,
              sx: { fontSize: 13 }
            }}
          />
          <Button
            variant="contained"
            size="small"
            startIcon={<AddIcon />}
            component={Link}
            href="/subject/create"
          >
            Create subject
          </Button>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {typeFilters.map((f) => (
              <Chip
                key={f}
                label={f === 'All' ? 'All' : f === 'USER' ? 'Users' : 'Clients'}
                size="small"
                variant={typeFilter === f ? 'filled' : 'outlined'}
                color={typeFilter === f ? 'primary' : 'default'}
                onClick={() => setTypeFilter(f)}
              />
            ))}
          </Box>
          <Select
            size="small"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value as RoleFilter)}
            sx={{ minWidth: 130, fontSize: 13 }}
          >
            {ROLE_FILTERS.map((r) => (
              <MenuItem key={r} value={r} sx={{ fontSize: 13 }}>{r === 'All' ? 'All Roles' : r}</MenuItem>
            ))}
          </Select>
          <Select
            size="small"
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
            sx={{ minWidth: 130, fontSize: 13 }}
          >
            {allDomains.map((d) => (
              <MenuItem key={d} value={d} sx={{ fontSize: 13 }}>{d === 'All' ? 'All Domains' : d}</MenuItem>
            ))}
          </Select>
        </Box>
      </Box>

      {/* Table */}
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel active={sortCol === 'subject_name'} direction={sortCol === 'subject_name' ? sortDir : 'asc'} onClick={handleSort}>
                  Name
                </TableSortLabel>
              </TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Subject ID</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sorted.length > 0 ? (
              sorted.map((subject, idx) => {
                const perms = permsBySubjectId[subject.subject_id as string]
                const role = deriveRole(perms)
                const isLoadingPerms = !perms && permissionQueries[data.indexOf(subject)]?.isLoading
                return (
                  <TableRow
                    key={idx}
                    hover
                    onClick={() =>
                      router.push({
                        pathname: `/subject/modify/${subject.subject_id}`,
                        query: { name: subject.subject_name, type: subject.type }
                      })
                    }
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell sx={{ fontWeight: 500, color: 'primary.main' }}>{subject.subject_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={subject.type === 'USER' ? 'User' : 'Client'}
                        size="small"
                        color={subject.type === 'USER' ? 'info' : 'success'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {isLoadingPerms
                        ? <Typography variant="body2" sx={{ fontSize: 11, color: 'text.disabled' }}>…</Typography>
                        : <Typography variant="body2" sx={{ fontSize: 12 }}>{role}</Typography>
                      }
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>{subject.subject_id}</TableCell>
                  </TableRow>
                )
              })
            ) : (
              <TableRow>
                <TableCell colSpan={4} sx={{ textAlign: 'center', py: 5, color: 'text.disabled', fontSize: 13 }}>
                  {data?.length === 0
                    ? 'No subjects found. Create one to get started.'
                    : 'No subjects match the current filters.'}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Footer */}
      <Box sx={{ px: '18px', py: '12px', borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="body2" sx={{ fontSize: 12 }}>
          {filtered.length} subject{filtered.length !== 1 ? 's' : ''}
          {filtered.length !== data?.length ? ` (of ${data?.length})` : ''}
        </Typography>
      </Box>
    </Paper>
  )
}

export default UserAdminPage

UserAdminPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="User Admin">{page}</AccountLayout>
)
