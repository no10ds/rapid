import { AccountLayout } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectPermissions } from '@/service'
import { Card, Stack, Typography, LinearProgress } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'

function SubjectModifyPageSuccess() {
  const router = useRouter()
  const { subjectId, name } = router.query

  const {
    isLoading: isSubjectPermissionsLoading,
    data: subjectPermissionsData,
    error: subjectPermissionsError
  } = useQuery(['subjectPermissions', subjectId], getSubjectPermissions, {
    staleTime: 0
  })

  if (isSubjectPermissionsLoading) {
    return <LinearProgress />
  }

  if (subjectPermissionsError) {
    return <ErrorCard error={subjectPermissionsError as Error} />
  }

  return (
    <Card>
      <Typography variant="h2" gutterBottom>
        Success
      </Typography>
      <Typography gutterBottom>Permissions modified for {name}</Typography>

      <Stack direction="column" spacing={2} sx={{ width: '100%', textAlign: 'center' }}>
        {subjectPermissionsData.map((item) => (
          <Typography key={item.name}>{item.name}</Typography>
        ))}
      </Stack>
    </Card>
  )
}

export default SubjectModifyPageSuccess

SubjectModifyPageSuccess.getLayout = (page) => (
  <AccountLayout title="Modify User">{page}</AccountLayout>
)
