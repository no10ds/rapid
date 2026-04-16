import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { ReactNode } from 'react'

function UserAdminPage() {
  const router = useRouter()
  const { isLoading, data, error } = useQuery(['subjectsList'], getSubjectsListUi)

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  return (
    <div>
      <div className="tbl-wrap">
        <div className="tbl-toolbar">
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', flex: 1 }}>
            Manage users and client applications.
          </p>
          <Link href="/subject/create" className="tb-btn">
            + Create subject
          </Link>
        </div>
        <table>
          <thead>
            <tr>
              <th>Subject Name</th>
              <th>Type</th>
              <th>Subject ID</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data && data.length > 0 ? (
              data.map((subject, idx) => (
                <tr key={idx}>
                  <td className="mn" style={{ fontWeight: 500 }}>
                    {subject.subject_name}
                  </td>
                  <td>
                    <span
                      className={`badge ${subject.type === 'USER' ? 'raw' : 'cur'}`}
                    >
                      {subject.type === 'USER' ? 'User' : 'Client'}
                    </span>
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
              ))
            ) : (
              <tr>
                <td
                  colSpan={4}
                  style={{
                    textAlign: 'center',
                    padding: '40px 20px',
                    color: 'var(--text-tertiary)',
                    fontSize: '13px'
                  }}
                >
                  No subjects found. Create one to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
        <div className="pager">
          <div className="pg-info">
            {data ? `${data.length} subject${data.length !== 1 ? 's' : ''}` : '0 subjects'}
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
