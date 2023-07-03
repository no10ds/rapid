import { Card, Row, Button, Select } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import AccountLayout from '@/components/Layout/AccountLayout'
import { getSubjectsListUi } from '@/service'
import { FilteredSubjectList } from '@/service/types'
import { FormControl, Typography, LinearProgress } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

function SubjectModifyPage() {
  const router = useRouter()
  const [selectedSubjectId, setSelectedSubjectId] = useState('')
  const [filteredSubjectListData, setFilteredSubjectListData] =
    useState<FilteredSubjectList>({ ClientApps: [], Users: [] })

  const {
    isLoading: isSubjectsListLoading,
    data: subjectsListData,
    error: subjectListError
  } = useQuery(['subjectsList'], getSubjectsListUi)

  useEffect(() => {
    if (subjectsListData) {
      const users = subjectsListData
        .filter((subject) => subject['type'] === 'USER')
        .map((subject) => ({
          subjectId: subject['subject_id'],
          subjectName: subject['subject_name']
        }))
        .sort((a, b) => a.subjectName.localeCompare(b.subjectName))

      const clients = subjectsListData
        .filter((subject) => subject['type'] === 'CLIENT')
        .map((subject) => ({
          subjectId: subject['subject_id'],
          subjectName: subject['subject_name']
        }))
        .sort((a, b) => a.subjectName.localeCompare(b.subjectName))

      setFilteredSubjectListData({ ClientApps: clients, Users: users })
      setSelectedSubjectId(clients[0].subjectId)
    }
  }, [subjectsListData])

  if (isSubjectsListLoading) {
    return <LinearProgress />
  }

  if (subjectListError) {
    return <ErrorCard error={subjectListError as Error} />
  }

  return (
    <Card
      action={
        <Button
          color="primary"
          data-testid="submit-button"
          onClick={() => {
            const subject = subjectsListData.filter(
              (item) => item.subject_id === selectedSubjectId
            )[0]
            router.push({
              pathname: `/subject/modify/${selectedSubjectId}`,
              query: {
                name: subject.subject_name
              }
            })
          }}
        >
          Next
        </Button>
      }
    >
      <Typography variant="body1" gutterBottom>
        Modify the permissions a user or client can have. Select the user or client from
        the list below and update their permissions on the next screen.
      </Typography>

      <Typography variant="h2" gutterBottom>
        Select Subject
      </Typography>

      <Row>
        <FormControl fullWidth size="small">
          <Select
            label="Select a Client App or User"
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
    </Card>
  )
}

export default SubjectModifyPage

SubjectModifyPage.getLayout = (page) => (
  <AccountLayout title="Modify User">{page}</AccountLayout>
)
