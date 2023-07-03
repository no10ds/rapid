import { useState } from 'react'
import { Card, Row, Chip, Button, TextField, Select, Alert } from '@/components'
import AccountLayout from '@/components/Layout/AccountLayout'
import { zodResolver } from '@hookform/resolvers/zod'
import { Stack, Typography, LinearProgress } from '@mui/material'
import { Controller, useForm } from 'react-hook-form'
import { z } from 'zod'
import { createClient, SubjectCreate } from '@/service'
import { getPermissionsListUi } from '@/service/fetch'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import {
  ClientCreateBody,
  UserCreateBody,
  ClientCreateResponse,
  UserCreateResponse
} from '@/service/types'
import ErrorCard from '@/components/ErrorCard/ErrorCard'

const userType = ['User', 'Client']

type UserCreate = z.infer<typeof SubjectCreate>

const permissionListKeyMapping = {
  ADMIN: 'Management Permissions',
  GLOBAL_READ: 'Global Read Permissions',
  GLOBAL_WRITE: 'Global Write Permissions',
  PROTECTED_READ: 'Read Protected Permissions',
  PROTECTED_WRITE: 'Write Protected Permissions'
}

function CreateUserPage() {
  const router = useRouter()
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])

  const {
    isLoading: isPermissionsListLoading,
    data: permissionsListData,
    error: permissionsListError
  } = useQuery(['permissionsList'], getPermissionsListUi)

  const { control, handleSubmit, watch } = useForm<UserCreate>({
    resolver: zodResolver(SubjectCreate)
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
    return <LinearProgress />
  }

  if (permissionsListError) {
    return <ErrorCard error={permissionsListError as Error} />
  }

  if (permissionsListData) {
    return (
      <form
        onSubmit={handleSubmit(async (data) => {
          const baseData = { permissions: selectedPermissions }
          if (data.type === 'User') {
            await mutate({
              path: 'user',
              data: {
                ...baseData,
                username: data.name,
                email: data.email
              }
            })
          } else if (data.type === 'Client') {
            await mutate({
              path: 'client',
              data: {
                ...baseData,
                client_name: data.name
              }
            })
          }
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
              Create subject
            </Button>
          }
        >
          <Typography variant="body1" gutterBottom>
            Create a new user or client using the rAPId instance. Simply fill out the form
            with the required information, which can be found in more detail at the link{' '}
            <a href="https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md#create-user">
              provided.
            </a>
          </Typography>

          <Typography variant="h2" gutterBottom>
            Populate User Info
          </Typography>

          <Row>
            <Controller
              name="type"
              control={control}
              render={({ field, fieldState: { error } }) => (
                <>
                  <Typography variant="caption" gutterBottom>
                    Type of Subject
                  </Typography>
                  <Select
                    {...field}
                    error={!!error}
                    helperText={error?.message}
                    native
                    inputProps={{
                      'data-testid': 'field-type'
                    }}
                  >
                    <option value="">Please select</option>
                    {userType.map((type) => (
                      <option key={type}>{type}</option>
                    ))}
                  </Select>
                </>
              )}
            />
          </Row>

          {watch('type') === 'User' ? (
            <Row>
              <Controller
                name="email"
                control={control}
                render={({ field, fieldState: { error } }) => (
                  <>
                    <Typography variant="caption" gutterBottom>
                      Email
                    </Typography>
                    <TextField
                      {...field}
                      fullWidth
                      size="small"
                      type="email"
                      inputProps={{
                        'data-testid': 'field-email'
                      }}
                      error={!!error ? !!error : watch('type') === 'User' && !field.value}
                      helperText={
                        watch('type') === 'User' && !field.value
                          ? 'Required'
                          : error?.message
                      }
                    />
                  </>
                )}
              />
            </Row>
          ) : null}

          <Row>
            <Controller
              name="name"
              control={control}
              render={({ field, fieldState: { error } }) => (
                <>
                  <Typography variant="caption" gutterBottom>
                    Name
                  </Typography>
                  <TextField
                    {...field}
                    fullWidth
                    size="small"
                    variant="outlined"
                    error={!!error}
                    helperText={error?.message}
                    inputProps={{
                      'data-testid': 'field-name'
                    }}
                  />
                </>
              )}
            />
          </Row>

          <Typography variant="h2" gutterBottom>
            Select Permissions
          </Typography>

          {Object.keys(permissionsListData).map((key, index) => {
            return (
              <Row key={index}>
                <Typography variant="caption" component="label" gutterBottom>
                  {permissionListKeyMapping[key]}
                </Typography>
                <Stack direction="row" spacing={2}>
                  {permissionsListData[key].map((item) => {
                    return (
                      <Chip
                        label={item.display_name}
                        key={item.display_name_full}
                        onToggle={(_e, active) => {
                          if (active) {
                            setSelectedPermissions([...selectedPermissions, item.name])
                          } else {
                            setSelectedPermissions(
                              selectedPermissions.filter((_item) => _item !== item.name)
                            )
                          }
                        }}
                        toggle
                      />
                    )
                  })}
                </Stack>
              </Row>
            )
          })}

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error?.message}
            </Alert>
          )}
        </Card>
      </form>
    )
  }

  return <></>
}

export default CreateUserPage

CreateUserPage.getLayout = (page) => (
  <AccountLayout title="Create User">{page}</AccountLayout>
)
