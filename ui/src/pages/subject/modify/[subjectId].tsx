import { Button, Card } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import AccountLayout from '@/components/Layout/AccountLayout'
import {
  getPermissionsListUi,
  getSubjectPermissions,
  updateSubjectPermissions
} from '@/service'
import { extractPermissionNames } from '@/service/permissions'
import {
  UpdateSubjectPermissionsBody,
  UpdateSubjectPermissionsResponse
} from '@/service/types'
import { Alert, Typography, LinearProgress } from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useEffect } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import PermissionsTable from '@/components/PermissionsTable/PermissionsTable'


function SubjectModifyPage() {
  const router = useRouter()
  const { subjectId, name } = router.query

  const { control, handleSubmit } = useForm()

  const fieldArrayReturn = useFieldArray({
    control,
    name: 'permissions'
  });

  const { append } = fieldArrayReturn;

  const {
    isLoading: isPermissionsListDataLoading,
    data: permissionsListData,
    error: permissionsListDataError
  } = useQuery(['permissionsList'], getPermissionsListUi)

  const {
    isLoading: isSubjectPermissionsLoading,
    data: subjectPermissionsData,
    error: subjectPermissionsError
  } = useQuery(['subjectPermissions', subjectId], getSubjectPermissions)

  useEffect(() => {
    if (subjectPermissionsData) {
      append(subjectPermissionsData)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subjectPermissionsData])

  const { isLoading, mutate, error } = useMutation<
    UpdateSubjectPermissionsResponse,
    Error,
    UpdateSubjectPermissionsBody
  >({
    mutationFn: updateSubjectPermissions,
    onSuccess: () => {
      router.push({ pathname: `/subject/modify/success/${subjectId}`, query: { name } })
    }
  })

  if (isPermissionsListDataLoading || isSubjectPermissionsLoading) {
    return <LinearProgress />
  }

  if (permissionsListDataError || subjectPermissionsError) {
    return (
      <ErrorCard
        error={(permissionsListDataError as Error) || (subjectPermissionsError as Error)}
      />
    )
  }

  return (
    <form
      onSubmit={handleSubmit(async (data) => {
        const permissions = data.permissions.map((permission) => extractPermissionNames(permission, permissionsListData))
        await mutate(
          { subject_id: subjectId as string, permissions })
      })}
      noValidate
    >
      <Card
        action={
          <Button
            color="primary"
            type="submit"
            loading={isLoading}
            data-testid="submit"
          >
            Modify
          </Button>
        }
      >
        <Typography variant="h2" gutterBottom>
          Modify Subject
        </Typography>
        <Typography gutterBottom>Select permissions for {name}</Typography>
        <PermissionsTable permissionsListData={permissionsListData} fieldArrayReturn={fieldArrayReturn} />
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error?.message}
          </Alert>
        )}
      </Card>
    </form>
  )
}

export default SubjectModifyPage

SubjectModifyPage.getLayout = (page) => (
  <AccountLayout title="Modify User">{page}</AccountLayout>
)
