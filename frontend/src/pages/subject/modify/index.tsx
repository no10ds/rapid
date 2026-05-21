import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectsListUi } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, useMemo, useEffect, ReactNode } from 'react'
import { filterSubjectList } from '@/utils/subject'
import {
  Box,
  Button,
  LinearProgress,
  Select,
  FormControl,
  InputLabel
} from '@mui/material'

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

  useEffect(() => {
    if (!selectedSubjectId && (users.length > 0 || clients.length > 0)) {
      setSelectedSubjectId(users[0]?.subjectId ?? clients[0]?.subjectId ?? '')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [users, clients])

  if (isLoading) return <LinearProgress color="primary" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  return (
    <Box sx={{ maxWidth: 860, mx: 'auto' }}>
      <FormCard
        title="Select subject"
        actions={
          <Button
            variant="contained"
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
          </Button>
        }
      >
        <FormControl size="small" sx={{ maxWidth: 360, width: '100%' }}>
          <InputLabel htmlFor="field-user" shrink>Subject</InputLabel>
          <Select
            native
            label="Subject"
            notched
            value={selectedSubjectId}
            onChange={(e) => setSelectedSubjectId(e.target.value as string)}
            inputProps={{ 'data-testid': 'field-user', id: 'field-user' }}
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
          </Select>
        </FormControl>
      </FormCard>
    </Box>
  )
}

export default SubjectModifyPage

SubjectModifyPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Modify Subject">{page}</AccountLayout>
)
