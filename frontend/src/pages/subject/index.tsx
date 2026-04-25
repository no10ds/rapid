import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi, getSubjectPermissions } from '@/service'
import { SubjectPermission } from '@/service/types'
import { useQuery, useQueries } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ReactNode, useState, useMemo } from 'react'

type SubjectType = 'All' | 'USER' | 'CLIENT'

type RoleFilter = 'All' | 'User Admin' | 'Data Admin' | 'Read/Write' | 'Read Only' | 'No Permissions'

const ROLE_FILTERS: RoleFilter[] = ['All', 'User Admin', 'Data Admin', 'Read/Write', 'Read Only', 'No Permissions']

function deriveRole(perms: SubjectPermission[] | undefined): RoleFilter {
  if (!perms || perms.length === 0) return 'No Permissions'
  const types = perms.map((p) => p.type).filter(Boolean)
  if (types.includes('USER_ADMIN')) return 'User Admin'
  if (types.includes('DATA_ADMIN')) return 'Data Admin'
  if (types.includes('WRITE')) return 'Read/Write'
  if (types.includes('READ')) return 'Read Only'
  return 'No Permissions'
}

function UserAdminPage() {
  const router = useRouter()
  const [typeFilter, setTypeFilter] = useState<SubjectType>('All')
  const [roleFilter, setRoleFilter] = useState<RoleFilter>('All')
  const [search, setSearch] = useState('')

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

  const filtered = useMemo(() => {
    if (!data) return []
    return data.filter((s) => {
      if (typeFilter !== 'All' && s.type !== typeFilter) return false
      if (search.trim()) {
        const q = search.trim().toLowerCase()
        if (!String(s.subject_name ?? '').toLowerCase().includes(q)) return false
      }
      if (roleFilter !== 'All') {
        const role = deriveRole(permsBySubjectId[s.subject_id as string])
        if (role !== roleFilter) return false
      }
      return true
    })
  }, [data, typeFilter, roleFilter, search, permsBySubjectId])

  if (isLoading) return <div className="rapid-loading-bar" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  const typeFilters: SubjectType[] = ['All', 'USER', 'CLIENT']

  return (
    <div>
      <div className="tbl-wrap">
        <div className="tbl-toolbar" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', width: '100%' }}>
            <input
              className="search-in"
              placeholder="Search by name…"
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ minWidth: '220px', flex: 1 }}
            />
            <Link href="/subject/create" className="tb-btn" style={{ textDecoration: 'none', whiteSpace: 'nowrap' }}>
              + Create subject
            </Link>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span className="cat-lbl">Type</span>
              <div style={{ display: 'flex', gap: '4px' }}>
                {typeFilters.map((f) => (
                  <button
                    key={f}
                    className={`fchip${typeFilter === f ? ' on' : ''}`}
                    onClick={() => setTypeFilter(f)}
                    type="button"
                  >
                    {f === 'All' ? 'All' : f === 'USER' ? 'Users' : 'Clients'}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span className="cat-lbl">Role</span>
              <select
                className="cat-sel"
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value as RoleFilter)}
              >
                {ROLE_FILTERS.map((r) => (
                  <option key={r}>{r}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Role</th>
              <th>Subject ID</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length > 0 ? (
              filtered.map((subject, idx) => {
                const perms = permsBySubjectId[subject.subject_id as string]
                const role = deriveRole(perms)
                const isLoadingPerms = !perms && permissionQueries[data.indexOf(subject)]?.isLoading
                return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 500 }}>{subject.subject_name}</td>
                    <td>
                      <span className={`badge ${subject.type === 'USER' ? 'raw' : 'cur'}`}>
                        {subject.type === 'USER' ? 'User' : 'Client'}
                      </span>
                    </td>
                    <td>
                      {isLoadingPerms
                        ? <span style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>…</span>
                        : <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{role}</span>
                      }
                    </td>
                    <td className="mn">{subject.subject_id}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <button
                          className="act-btn"
                          type="button"
                          onClick={() =>
                            router.push({
                              pathname: `/subject/modify/${subject.subject_id}`,
                              query: { name: subject.subject_name }
                            })
                          }
                        >
                          Edit
                        </button>
                        <button
                          className="act-btn act-btn-del"
                          type="button"
                          onClick={() => router.push('/subject/delete')}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })
            ) : (
              <tr>
                <td
                  colSpan={5}
                  style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-tertiary)', fontSize: '13px' }}
                >
                  {data?.length === 0
                    ? 'No subjects found. Create one to get started.'
                    : 'No subjects match the current filters.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>

        <div className="pager">
          <div className="pg-info">
            {filtered.length} subject{filtered.length !== 1 ? 's' : ''}
            {filtered.length !== data?.length ? ` (of ${data?.length})` : ''}
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserAdminPage

UserAdminPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="User Admin">{page}</AccountLayout>
)
