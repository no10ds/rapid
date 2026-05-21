import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi } from '@/service'
import { FilteredSubjectList } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { filterSubjectList } from '@/utils/subject'
import { useEffect, useState, ReactNode } from 'react'
import { deleteUser as deleteUserFn, deleteClient as deleteClientFn } from '@/service'
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  TextField,
  Select,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'

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
    return <LinearProgress color="primary" role="progressbar" />
  }

  return (
    <Box sx={{ maxWidth: 860, mx: 'auto' }}>
      <FormCard
        title="Select subject to delete"
        actions={
          <Button
            variant="contained"
            color="error"
            data-testid="delete-button"
            onClick={() => setIsConfirmDeleteDialogOpen(true)}
          >
            Delete
          </Button>
        }
      >
        <Typography variant="body2" sx={{ fontSize: 13, mb: 2 }}>
          Delete an existing user or client.
        </Typography>
        <FormControl size="small" fullWidth>
          <InputLabel htmlFor="field-user" shrink>Select a Client or User</InputLabel>
          <Select
            native
            label="Select a Client or User"
            notched
            value={selectedSubjectId}
            onChange={(event) => setSelectedSubjectId(event.target.value as string)}
            inputProps={{ 'data-testid': 'field-user', id: 'field-user' }}
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
      </FormCard>

      <Dialog
        open={isConfirmDeleteDialogOpen}
        onClose={() => setIsConfirmDeleteDialogOpen(false)}
        data-testid="delete-confirmation-dialog"
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ fontSize: 16, fontWeight: 600 }}>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ fontSize: 13, mb: 1 }}>
            This action cannot be undone. Please type in the name of the subject to confirm.
          </Typography>
          <Typography sx={{ fontSize: 12, fontStyle: 'italic', mb: 2 }}>
            {getCurrentSelectedSubjectName()}
          </Typography>
          <TextField
            size="small"
            fullWidth
            value={userConfirmation}
            onChange={(e) => setUserConfirmation(e.target.value)}
            placeholder="Type subject name to confirm"
            inputProps={{ 'data-testid': 'field-user-confirmation' }}
          />
        </DialogContent>
        <DialogActions>
          <Button variant="outlined" onClick={() => setIsConfirmDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={deleteSubject}
            disabled={
              isUserDeleting ||
              isClientDeleting ||
              userConfirmation !== getCurrentSelectedSubjectName()
            }
            data-testid="delete-confirmation-dialog-delete-button"
          >
            {isUserDeleting || isClientDeleting ? 'Deleting…' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DeleteSubject

DeleteSubject.getLayout = (page: ReactNode) => (
  <AccountLayout title="Delete User">{page}</AccountLayout>
)
