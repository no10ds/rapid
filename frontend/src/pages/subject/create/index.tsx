import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import PermissionsTable from '@/components/PermissionsTable/PermissionsTable'
import { zodResolver } from '@hookform/resolvers/zod'
import { Controller, useForm, useFieldArray } from 'react-hook-form'
import { z } from 'zod'
import { createClient, SubjectCreate } from '@/service'
import { extractPermissionNames } from '@/service/permissions'
import { getPermissionsListUi } from '@/service/fetch'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import {
  ClientCreateBody,
  UserCreateBody,
  ClientCreateResponse,
  UserCreateResponse
} from '@/service/types'
import { ReactNode } from 'react'
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  TextField,
  Select,
  FormControl,
  InputLabel,
  FormHelperText
} from '@mui/material'

const userType = ['User', 'Client']

type UserCreate = z.infer<typeof SubjectCreate>

function CreateUserPage() {
  const router = useRouter()

  const {
    isLoading: isPermissionsListLoading,
    data: permissionsListData,
    error: permissionsListError
  } = useQuery(['permissionsList'], getPermissionsListUi)

  const { control, handleSubmit, watch } = useForm<UserCreate>({
    resolver: zodResolver(SubjectCreate)
  })

  const fieldArrayReturn = useFieldArray({
    control,
    name: 'permissions'
  })

  const { isLoading, mutate, error } = useMutation<
    ClientCreateResponse | UserCreateResponse,
    Error,
    { path: string; data: ClientCreateBody | UserCreateBody }
  >({
    mutationFn: createClient,
    onSuccess: (data, variables) => {
      let query = {}
      if (variables.path === 'client') {
        const response = data as ClientCreateResponse
        query = {
          Client: response.client_name,
          Id: response.client_id,
          Secret: response.client_secret
        }
      } else if (variables.path === 'user') {
        const response = data as UserCreateResponse
        query = {
          User: response.username,
          Id: response.user_id,
          Email: response.email
        }
      }
      router.push({ pathname: '/subject/create/success/', query })
    }
  })

  if (isPermissionsListLoading) {
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (permissionsListError) {
    return <ErrorCard error={permissionsListError as Error} />
  }

  if (!permissionsListData) {
    return <></>
  }

  return (
    <Box
      component="form"
      sx={{ maxWidth: 900, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}
      onSubmit={handleSubmit(async (data: UserCreate) => {
        const permissions = data.permissions.map((permission) =>
          extractPermissionNames(permission, permissionsListData)
        )
        if (data.type === 'User') {
          await mutate({
            path: 'user',
            data: { permissions, username: data.name, email: data.email }
          })
        } else if (data.type === 'Client') {
          await mutate({
            path: 'client',
            data: { permissions, client_name: data.name }
          })
        }
      })}
      noValidate
    >
      <FormCard num={1} title="Subject info">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="body2" sx={{ fontSize: 13 }}>
            Create a new user or client. For more details see the{' '}
            <Box
              component="a"
              href="https://rapid.readthedocs.io/en/latest/api/routes/user/#create"
              sx={{ color: 'primary.main', textDecoration: 'none' }}
            >
              documentation
            </Box>
            .
          </Typography>

          <Controller
            name="type"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <FormControl size="small" error={!!fieldError} fullWidth>
                <InputLabel htmlFor="field-type" shrink>Type of Subject</InputLabel>
                <Select
                  {...field}
                  native
                  label="Type of Subject"
                  notched
                  inputProps={{ 'data-testid': 'field-type', id: 'field-type' }}
                  value={field.value ?? ''}
                >
                  <option value="">Please select</option>
                  {userType.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </Select>
                {fieldError && <FormHelperText>{fieldError.message}</FormHelperText>}
              </FormControl>
            )}
          />

          {watch('type') === 'User' && (
            <Controller
              name="email"
              control={control}
              render={({ field, fieldState: { error: fieldError } }) => (
                <TextField
                  {...field}
                  size="small"
                  label="Email"
                  type="email"
                  error={!!fieldError}
                  helperText={fieldError?.message}
                  inputProps={{ 'data-testid': 'field-email', id: 'field-email' }}
                  InputLabelProps={{ shrink: true }}
                />
              )}
            />
          )}

          <Controller
            name="name"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <TextField
                {...field}
                size="small"
                label="Name"
                error={!!fieldError}
                helperText={fieldError?.message}
                inputProps={{ 'data-testid': 'field-name', id: 'field-name' }}
                InputLabelProps={{ shrink: true }}
              />
            )}
          />
        </Box>
      </FormCard>

      <FormCard
        num={2}
        title="Select permissions"
        bodySx={{ p: 0 }}
        actionsError={error}
        actions={
          <Button variant="contained" type="submit" data-testid="submit" disabled={isLoading}>
            {isLoading ? 'Creating…' : 'Create subject'}
          </Button>
        }
      >
        <PermissionsTable
          permissionsListData={permissionsListData}
          fieldArrayReturn={fieldArrayReturn}
        />
      </FormCard>
    </Box>
  )
}

export default CreateUserPage

CreateUserPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Create User">{page}</AccountLayout>
)
