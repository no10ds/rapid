import { AccountLayout, Card } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getSubjectPermissions } from '@/service'
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
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (subjectPermissionsError) {
    return <ErrorCard error={subjectPermissionsError as Error} />
  }

  return (
    <Card>
      <h2>Success</h2>
      <p>Permissions modified for {name}</p>

      <ul style={{ listStyle: 'none', padding: 0, textAlign: 'center' }}>
        {subjectPermissionsData.map((item) => (
          <li key={item.id}>{item.id}</li>
        ))}
      </ul>
    </Card>
  )
}

export default SubjectModifyPageSuccess

SubjectModifyPageSuccess.getLayout = (page) => (
  <AccountLayout title="Modify User">{page}</AccountLayout>
)
