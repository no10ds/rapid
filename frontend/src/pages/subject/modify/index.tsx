import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, useMemo, useEffect, ReactNode } from 'react'
import { filterSubjectList } from '@/utils/subject'

function SubjectModifyPage() {
  const router = useRouter()
  const [selectedSubjectId, setSelectedSubjectId] = useState('')

  const { isLoading, data: subjectsListData, error } = useQuery(
    ['subjectsList'],
    getSubjectsListUi
  )

  const users = useMemo(
    () => (subjectsListData ? filterSubjectList(subjectsListData, 'USER') : []),
    [subjectsListData]
  )

  const clients = useMemo(
    () => (subjectsListData ? filterSubjectList(subjectsListData, 'CLIENT') : []),
    [subjectsListData]
  )

  // Set initial selection once data arrives
  useEffect(() => {
    if (!selectedSubjectId && (users.length > 0 || clients.length > 0)) {
      setSelectedSubjectId(users[0]?.subjectId ?? clients[0]?.subjectId ?? '')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [users, clients])

  if (isLoading) return <div className="rapid-loading-bar" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  return (
    <div style={{ maxWidth: 860, margin: '0 auto' }}>
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Select subject</div>
        </div>
        <div className="form-card-body">
          <div className="field-row" style={{ marginBottom: 0 }}>
            <label className="f-lbl" htmlFor="field-user">Subject</label>
            <select
              id="field-user"
              className="f-sel"
              style={{ maxWidth: 360 }}
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value)}
              data-testid="field-user"
            >
              {users.length > 0 && (
                <optgroup label="Users">
                  {users.map((item) => (
                    <option value={item.subjectId} key={item.subjectId}>
                      {item.subjectName}
                    </option>
                  ))}
                </optgroup>
              )}
              {clients.length > 0 && (
                <optgroup label="Client Apps">
                  {clients.map((item) => (
                    <option value={item.subjectId} key={item.subjectId}>
                      {item.subjectName}
                    </option>
                  ))}
                </optgroup>
              )}
            </select>
          </div>
        </div>
        <div className="form-actions">
          <button
            className="btn-primary"
            type="button"
            data-testid="submit-button"
            disabled={!selectedSubjectId}
            onClick={() => {
              const subject = subjectsListData.find(
                (item) => item.subject_id === selectedSubjectId
              )
              router.push({
                pathname: `/subject/modify/${selectedSubjectId}`,
                query: { name: subject?.subject_name }
              })
            }}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}

export default SubjectModifyPage

SubjectModifyPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Modify Subject">{page}</AccountLayout>
)
