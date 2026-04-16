import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi } from '@/service'
import { FilteredSubjectList } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { filterSubjectList } from '@/utils/subject'
import { useEffect, useState, ReactNode } from 'react'
import { deleteUser as deleteUserFn, deleteClient as deleteClientFn } from '@/service'

function DeleteSubject() {
  const [selectedSubjectId, setSelectedSubjectId] = useState('')
  const [filteredSubjectListData, setFilteredSubjectListData] =
    useState<FilteredSubjectList>({ ClientApps: [], Users: [] })
  const [isConfirmDeleteDialogOpen, setIsConfirmDeleteDialogOpen] = useState(false)
  const [userConfirmation, setUserConfirmation] = useState('')

  const {
    isLoading: isSubjectsListLoading,
    data: subjectsListData,
    error: subjectsListError,
    refetch: refetchSubjectsList
  } = useQuery(['subjectsList'], getSubjectsListUi)

  const { isLoading: isUserDeleting, mutate: deleteUser } = useMutation<
    Response,
    Error,
    { userId: string; username: string }
  >({
    mutationFn: deleteUserFn,
    onSuccess: () => closeConfirmationAndRefetchUsers()
  })

  const { isLoading: isClientDeleting, mutate: deleteClient } = useMutation<
    Response,
    Error,
    { clientId: string }
  >({
    mutationFn: deleteClientFn,
    onSuccess: () => closeConfirmationAndRefetchUsers()
  })

  useEffect(() => {
    if (subjectsListData) {
      const users = filterSubjectList(subjectsListData, 'USER')
      const clients = filterSubjectList(subjectsListData, 'CLIENT')

      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFilteredSubjectListData({ ClientApps: clients, Users: users })
      setSelectedSubjectId(clients[0].subjectId)
    }
  }, [subjectsListData])

  useEffect(() => {
    if (isConfirmDeleteDialogOpen) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setUserConfirmation('')
    }
  }, [isConfirmDeleteDialogOpen])

  const closeConfirmationAndRefetchUsers = () => {
    setIsConfirmDeleteDialogOpen(false)
    setSelectedSubjectId('')
    refetchSubjectsList()
  }

  const deleteSubject = () => {
    const subject = subjectsListData.filter(
      (item) => item.subject_id === selectedSubjectId
    )[0]
    const { type, subject_id } = subject
    if (type === 'CLIENT') deleteClient({ clientId: subject_id })
    if (type === 'USER') deleteUser({ userId: subject_id, username: subject.subject_name })
  }

  const getCurrentSelectedSubjectName = () => {
    return subjectsListData.filter((item) => item.subject_id === selectedSubjectId)[0]
      ?.subject_name ?? ''
  }

  if (subjectsListError) {
    return <ErrorCard error={subjectsListError as Error} />
  }

  if (isSubjectsListLoading || !selectedSubjectId) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  return (
    <div className="form-wrap-wide">
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Select subject to delete</div>
        </div>
        <div className="form-card-body">
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Delete an existing user or client.
          </p>
          <div className="field-row">
            <label className="f-lbl" htmlFor="field-user">
              Select a Client or User
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
            className="btn-danger"
            type="button"
            data-testid="delete-button"
            onClick={() => setIsConfirmDeleteDialogOpen(true)}
          >
            Delete
          </button>
        </div>
      </div>

      {/* Confirmation modal */}
      {isConfirmDeleteDialogOpen && (
        <div
          className="modal-overlay"
          data-testid="delete-confirmation-dialog"
          role="dialog"
          aria-modal="true"
        >
          <div className="modal-box">
            <div className="modal-hd">Confirm Delete</div>
            <div className="modal-body">
              <p
                style={{
                  fontSize: '13px',
                  color: 'var(--text-secondary)',
                  marginBottom: '10px'
                }}
              >
                This action cannot be undone. Please type in the name of the subject to
                confirm.
              </p>
              <p
                style={{
                  fontSize: '12px',
                  fontStyle: 'italic',
                  color: 'var(--text-primary)',
                  marginBottom: '12px'
                }}
              >
                {getCurrentSelectedSubjectName()}
              </p>
              <input
                className="f-sel"
                value={userConfirmation}
                onChange={(e) => setUserConfirmation(e.target.value)}
                data-testid="field-user-confirmation"
                placeholder="Type subject name to confirm"
              />
            </div>
            <div className="modal-foot">
              <button
                className="btn-secondary"
                type="button"
                onClick={() => setIsConfirmDeleteDialogOpen(false)}
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                type="button"
                onClick={deleteSubject}
                disabled={
                  isUserDeleting ||
                  isClientDeleting ||
                  userConfirmation !== getCurrentSelectedSubjectName()
                }
                data-testid="delete-confirmation-dialog-delete-button"
              >
                {isUserDeleting || isClientDeleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DeleteSubject

DeleteSubject.getLayout = (page: ReactNode) => (
  <AccountLayout title="Delete User">{page}</AccountLayout>
)
