import { AccountLayout, Card, Button, Row, Select, TextField } from '@/components'
import { getSubjectsListUi } from '@/service'
import {
  DialogActions,
  DialogContent,
  FormControl,
  LinearProgress,
  Typography
} from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { filterSubjectList } from '@/utils/subject'
import { useEffect, useState } from 'react'
import { FilteredSubjectList } from '@/service/types'
import { deleteUser as deleteUserFn, deleteClient as deleteClientFn } from '@/service'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import Dialog from '@/components/Dialog/Dialog'

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

      setFilteredSubjectListData({ ClientApps: clients, Users: users })
      setSelectedSubjectId(clients[0].subjectId)
    }
  }, [subjectsListData])

  useEffect(() => {
    if (isConfirmDeleteDialogOpen) {
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
    if (type === 'USER')
      deleteUser({ userId: subject_id, username: subject.subject_name })
  }

  const getCurrentSelectedSubjectName = () => {
    return subjectsListData.filter((item) => item.subject_id === selectedSubjectId)[0]
      .subject_name
  }

  if (subjectsListError) {
    return <ErrorCard error={subjectsListError as Error} />
  }

  if (isSubjectsListLoading || !selectedSubjectId) {
    return <LinearProgress />
  }

  return (
    <Card
      action={
        <Button
          color="primary"
          data-testid="delete-button"
          onClick={() => {
            setIsConfirmDeleteDialogOpen(true)
          }}
        >
          Delete
        </Button>
      }
    >
      <Typography variant="body1" gutterBottom>
        Delete an existing user or client.
      </Typography>
      <Typography variant="h2" gutterBottom>
        Select Subject
      </Typography>

      <Row>
        <FormControl fullWidth size="small">
          <Select
            label="Select a Client or User"
            onChange={(event) => setSelectedSubjectId(event.target.value as string)}
            inputProps={{ 'data-testid': 'field-user' }}
            native
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
          </Select>
        </FormControl>
      </Row>

      <Dialog
        open={isConfirmDeleteDialogOpen}
        title="Confirm Delete"
        data-testid="delete-confirmation-dialog"
      >
        <DialogContent dividers>
          <Typography variant="body1" gutterBottom>
            This action cannot be undone. Please type in the name of the subject to
            confirm.
          </Typography>
          <Typography variant="body2" style={{ fontStyle: 'italic' }} gutterBottom>
            {getCurrentSelectedSubjectName()}
          </Typography>
          <TextField
            fullWidth
            size="small"
            variant="outlined"
            inputProps={{
              'data-testid': 'field-user-confirmation'
            }}
            value={userConfirmation}
            onChange={(e) => setUserConfirmation(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button color="secondary" onClick={() => setIsConfirmDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            color="primary"
            onClick={deleteSubject}
            loading={isUserDeleting || isClientDeleting}
            disabled={userConfirmation !== getCurrentSelectedSubjectName()}
            data-testid="delete-confirmation-dialog-delete-button"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  )
}

export default DeleteSubject

DeleteSubject.getLayout = (page) => (
  <AccountLayout title="Delete User">{page}</AccountLayout>
)
