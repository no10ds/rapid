import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi } from '@/service'
import { FilteredSubjectList } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useEffect, useState, ReactNode } from 'react'
import { filterSubjectList } from '@/utils/subject'

function SubjectModifyPage() {
  const router = useRouter()
  const [selectedSubjectId, setSelectedSubjectId] = useState('')
  const [filteredSubjectListData, setFilteredSubjectListData] =
    useState<FilteredSubjectList>({ ClientApps: [], Users: [] })

  const {
    isLoading: isSubjectsListLoading,
    data: subjectsListData,
    error: subjectsListError
  } = useQuery(['subjectsList'], getSubjectsListUi)

  useEffect(() => {
    if (subjectsListData) {
      const users = filterSubjectList(subjectsListData, 'USER')
      const clients = filterSubjectList(subjectsListData, 'CLIENT')

      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFilteredSubjectListData({ ClientApps: clients, Users: users })
      setSelectedSubjectId(clients[0].subjectId)
    }
  }, [subjectsListData])

  if (isSubjectsListLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (subjectsListError) {
    return <ErrorCard error={subjectsListError as Error} />
  }

  return (
    <div className="form-wrap-wide">
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Select subject to modify</div>
        </div>
        <div className="form-card-body">
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Modify the permissions a user or client can have. Select the user or client from
            the list below and update their permissions on the next screen.
          </p>
          <div className="field-row">
            <label className="f-lbl" htmlFor="field-user">
              Select a Client App or User
            </label>
            <select
              id="field-user"
              className="subject-sel"
              onChange={(event) => setSelectedSubjectId(event.target.value)}
              data-testid="field-user"
            >
              <optgroup label="Client Apps">
                {filteredSubjectListData.ClientApps.map((item) => (
                  <option value={item.subjectId} key={item.subjectId}>
                    {item.subjectName}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Users">
                {filteredSubjectListData.Users.map((item) => (
                  <option value={item.subjectId} key={item.subjectId}>
                    {item.subjectName}
                  </option>
                ))}
              </optgroup>
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
              const subject = subjectsListData.filter(
                (item) => item.subject_id === selectedSubjectId
              )[0]
              router.push({
                pathname: `/subject/modify/${selectedSubjectId}`,
                query: { name: subject.subject_name }
              })
            }}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}

export default SubjectModifyPage

SubjectModifyPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Modify User">{page}</AccountLayout>
)
