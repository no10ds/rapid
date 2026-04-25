import AccountLayout from '@/components/Layout/AccountLayout'
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
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (permissionsListError) {
    return <ErrorCard error={permissionsListError as Error} />
  }

  if (!permissionsListData) {
    return <></>
  }

  return (
    <form
      className="form-wrap-wide"
      onSubmit={handleSubmit(async (data: UserCreate) => {
        const permissions = data.permissions.map((permission) =>
          extractPermissionNames(permission, permissionsListData)
        )
        if (data.type === 'User') {
          await mutate({
            path: 'user',
            data: {
              permissions: permissions,
              username: data.name,
              email: data.email
            }
          })
        } else if (data.type === 'Client') {
          await mutate({
            path: 'client',
            data: {
              permissions: permissions,
              client_name: data.name
            }
          })
        }
      })}
      noValidate
    >
      {/* Card 1 — Subject info */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Subject info</div>
        </div>
        <div className="form-card-body">
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Create a new user or client. For more details see the{' '}
            <a
              href="https://rapid.readthedocs.io/en/latest/api/routes/user/#create"
              style={{ color: 'var(--pink)', textDecoration: 'none' }}
            >
              documentation
            </a>
            .
          </p>

          <Controller
            name="type"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <div className="field-row">
                <label className="f-lbl" htmlFor="field-type">
                  Type of Subject
                </label>
                <select
                  {...field}
                  id="field-type"
                  className="f-sel"
                  data-testid="field-type"
                  style={fieldError ? { borderColor: 'var(--red)' } : undefined}
                >
                  <option value="">Please select</option>
                  {userType.map((type) => (
                    <option key={type}>{type}</option>
                  ))}
                </select>
                {fieldError && (
                  <span className="f-hint" style={{ color: 'var(--red)' }}>
                    {fieldError.message}
                  </span>
                )}
              </div>
            )}
          />

          {watch('type') === 'User' && (
            <Controller
              name="email"
              control={control}
              render={({ field, fieldState: { error: fieldError } }) => (
                <div className="field-row">
                  <label className="f-lbl" htmlFor="field-email">
                    Email
                  </label>
                  <input
                    {...field}
                    id="field-email"
                    className="f-sel"
                    type="email"
                    data-testid="field-email"
                    style={fieldError ? { borderColor: 'var(--red)' } : undefined}
                  />
                  {fieldError && (
                    <span className="f-hint" style={{ color: 'var(--red)' }}>
                      {fieldError.message}
                    </span>
                  )}
                </div>
              )}
            />
          )}

          <Controller
            name="name"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <div className="field-row">
                <label className="f-lbl" htmlFor="field-name">
                  Name
                </label>
                <input
                  {...field}
                  id="field-name"
                  className="f-sel"
                  data-testid="field-name"
                  style={fieldError ? { borderColor: 'var(--red)' } : undefined}
                />
                {fieldError && (
                  <span className="f-hint" style={{ color: 'var(--red)' }}>
                    {fieldError.message}
                  </span>
                )}
              </div>
            )}
          />
        </div>
      </div>

      {/* Card 2 — Permissions */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">2</div>
          <div className="form-card-title">Select permissions</div>
        </div>
        <div className="form-card-body" style={{ padding: 0 }}>
          <PermissionsTable
            permissionsListData={permissionsListData}
            fieldArrayReturn={fieldArrayReturn}
          />
        </div>
        <div className="form-actions">
          <button
            className="btn-primary"
            type="submit"
            data-testid="submit"
            disabled={isLoading}
          >
            {isLoading ? 'Creating…' : 'Create subject'}
          </button>
          {error && (
            <span className="f-hint" style={{ color: 'var(--red)', marginLeft: '8px' }}>
              {error?.message}
            </span>
          )}
        </div>
      </div>
    </form>
  )
}

export default CreateUserPage

CreateUserPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Create User">{page}</AccountLayout>
)
