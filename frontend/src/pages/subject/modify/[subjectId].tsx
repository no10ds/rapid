import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import {
  getPermissionsListUi,
  getSubjectPermissions,
  updateSubjectPermissions,
  deleteUser as deleteUserFn,
  deleteClient as deleteClientFn
} from '@/service'
import { Permission, ActionEnum, SensitivityEnum } from '@/service'
import { extractPermissionNames } from '@/service/permissions'
import { UpdateSubjectPermissionsBody, UpdateSubjectPermissionsResponse } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useEffect, useState, ReactNode } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { cloneDeep } from 'lodash'
import Link from 'next/link'
import { z } from 'zod'
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Typography,
  LinearProgress,
  Alert,
  Select,
  MenuItem
} from '@mui/material'

type PermissionType = z.infer<typeof Permission>
type ActionType = z.infer<typeof ActionEnum>
type SensitivityType = z.infer<typeof SensitivityEnum>

function SubjectModifyPage() {
  const router = useRouter()
  const { subjectId, name, type: subjectType } = router.query

  const { control, handleSubmit } = useForm()
  const fieldArrayReturn = useFieldArray({ control, name: 'permissions' })
  const { fields, append, remove } = fieldArrayReturn

  const [addType, setAddType] = useState<ActionType | ''>('')
  const [addLayer, setAddLayer] = useState('')
  const [addSensitivity, setAddSensitivity] = useState<SensitivityType | ''>('')
  const [addDomain, setAddDomain] = useState('')
  const [addError, setAddError] = useState('')

  const {
    isLoading: isPermissionsListLoading,
    data: permissionsListData,
    error: permissionsListError
  } = useQuery(['permissionsList'], getPermissionsListUi)

  const {
    isLoading: isSubjectPermsLoading,
    data: subjectPermsData,
    error: subjectPermsError
  } = useQuery(['subjectPermissions', subjectId], getSubjectPermissions)

  useEffect(() => {
    if (subjectPermsData) {
      fieldArrayReturn.append(subjectPermsData)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subjectPermsData])

  const { isLoading: isSaving, mutate, error: saveError } = useMutation<
    UpdateSubjectPermissionsResponse,
    Error,
    UpdateSubjectPermissionsBody
  >({
    mutationFn: updateSubjectPermissions,
    onSuccess: () => {
      router.push({ pathname: `/subject/modify/success/${subjectId}`, query: { name } })
    }
  })

  const { isLoading: isDeleting, mutate: doDelete, error: deleteError } = useMutation<
    Response,
    Error,
    void
  >({
    mutationFn: async () => {
      if (subjectType === 'CLIENT') {
        return deleteClientFn({ clientId: subjectId as string })
      }
      return deleteUserFn({ userId: subjectId as string, username: name as string })
    },
    onSuccess: () => {
      router.push('/subject')
    }
  })

  if (isPermissionsListLoading || isSubjectPermsLoading) {
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (permissionsListError || subjectPermsError) {
    return <ErrorCard error={(permissionsListError || subjectPermsError) as Error} />
  }

  let filteredPerms = cloneDeep(permissionsListData)
  try {
    ;(fields as unknown as PermissionType[]).forEach((perm) => {
      filteredPerms = removePermOption(perm, filteredPerms)
    })
  } catch {
    // tolerate conflicts gracefully
  }

  const availableTypes = Object.keys(filteredPerms ?? {})
  const availableLayers = addType && filteredPerms?.[addType]
    ? Object.keys(filteredPerms[addType] as object)
    : []
  const availableSensitivities = addType && addLayer && (filteredPerms?.[addType] as Record<string, unknown>)?.[addLayer]
    ? Object.keys((filteredPerms[addType] as Record<string, Record<string, unknown>>)[addLayer])
    : []
  const availableDomains = addType && addLayer && addSensitivity === 'PROTECTED' &&
    (filteredPerms?.[addType] as Record<string, Record<string, Record<string, unknown>>>)?.[addLayer]?.['PROTECTED']
    ? Object.keys((filteredPerms[addType] as Record<string, Record<string, Record<string, unknown>>>)[addLayer]['PROTECTED'])
    : []

  const isAdminType = addType === 'DATA_ADMIN' || addType === 'USER_ADMIN'
  const canAdd = addType !== '' && (isAdminType || (addLayer && addSensitivity && (addSensitivity !== 'PROTECTED' || addDomain)))

  function handleAdd() {
    setAddError('')
    if (!canAdd) {
      setAddError('Please fill in all required fields.')
      return
    }
    const perm: PermissionType = isAdminType
      ? { type: addType as 'DATA_ADMIN' | 'USER_ADMIN', layer: undefined, sensitivity: undefined, domain: undefined }
      : { type: addType as 'READ' | 'WRITE', layer: addLayer, sensitivity: addSensitivity as SensitivityType, domain: addSensitivity === 'PROTECTED' ? addDomain : undefined }
    append(perm)
    setAddType('')
    setAddLayer('')
    setAddSensitivity('')
    setAddDomain('')
  }

  return (
    <Box sx={{ maxWidth: 860, mx: 'auto' }}>
      <form
        onSubmit={handleSubmit(async (data: { permissions: PermissionType[] }) => {
          const permissions = (data.permissions ?? []).map((p) =>
            extractPermissionNames(p, permissionsListData)
          )
          await mutate({ subject_id: subjectId as string, permissions })
        })}
        noValidate
      >
        <FormCard
          title={
            <>
              Edit permissions —{' '}
              <Typography component="span" sx={{ fontWeight: 400, fontFamily: "'DM Mono', monospace", fontSize: 12 }}>
                {name as string}
              </Typography>
            </>
          }
          bodySx={{ p: 0 }}
          actionsError={saveError}
          actions={
            <>
              <Button variant="contained" type="submit" disabled={isSaving} data-testid="submit">
                {isSaving ? 'Saving…' : 'Save changes'}
              </Button>
              <Button variant="outlined" component={Link} href="/subject">
                Cancel
              </Button>
            </>
          }
        >
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell>Layer</TableCell>
                  <TableCell>Sensitivity</TableCell>
                  <TableCell>Domain</TableCell>
                  <TableCell sx={{ width: 80 }}></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(fields as unknown as PermissionType[]).map((perm, idx) => (
                  <TableRow key={idx}>
                    <TableCell sx={{ fontSize: 12 }}>{perm.type}</TableCell>
                    <TableCell sx={{ fontSize: 12, color: perm.layer ? 'text.primary' : 'text.disabled' }}>{perm.layer ?? '—'}</TableCell>
                    <TableCell sx={{ fontSize: 12, color: perm.sensitivity ? 'text.primary' : 'text.disabled' }}>{perm.sensitivity ?? '—'}</TableCell>
                    <TableCell sx={{ fontSize: 12, color: perm.domain ? 'text.primary' : 'text.disabled' }}>{perm.domain ?? '—'}</TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        color="error"
                        onClick={() => remove(idx)}
                        sx={{ fontSize: 11, minWidth: 0 }}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}

                {availableTypes.length > 0 && (
                  <TableRow sx={{ bgcolor: '#f9fafb', borderTop: '2px dashed #e5e7eb' }}>
                    <TableCell>
                      <Select
                        size="small"
                        value={addType}
                        onChange={(e) => { setAddType(e.target.value as ActionType | ''); setAddLayer(''); setAddSensitivity(''); setAddDomain('') }}
                        displayEmpty
                        sx={{ fontSize: 12, width: '100%' }}
                        data-testid="select-type"
                      >
                        <MenuItem value="" sx={{ fontSize: 12 }}>Select type…</MenuItem>
                        {availableTypes.map((t) => <MenuItem key={t} value={t} sx={{ fontSize: 12 }}>{t}</MenuItem>)}
                      </Select>
                    </TableCell>
                    <TableCell>
                      {addType && !isAdminType && (
                        <Select
                          size="small"
                          value={addLayer}
                          onChange={(e) => { setAddLayer(e.target.value); setAddSensitivity(''); setAddDomain('') }}
                          displayEmpty
                          sx={{ fontSize: 12, width: '100%' }}
                          data-testid="select-layer"
                        >
                          <MenuItem value="" sx={{ fontSize: 12 }}>Select layer…</MenuItem>
                          {availableLayers.map((l) => <MenuItem key={l} value={l} sx={{ fontSize: 12 }}>{l}</MenuItem>)}
                        </Select>
                      )}
                    </TableCell>
                    <TableCell>
                      {addLayer && !isAdminType && (
                        <Select
                          size="small"
                          value={addSensitivity}
                          onChange={(e) => { setAddSensitivity(e.target.value as SensitivityType | ''); setAddDomain('') }}
                          displayEmpty
                          sx={{ fontSize: 12, width: '100%' }}
                          data-testid="select-sensitivity"
                        >
                          <MenuItem value="" sx={{ fontSize: 12 }}>Select sensitivity…</MenuItem>
                          {availableSensitivities.map((s) => <MenuItem key={s} value={s} sx={{ fontSize: 12 }}>{s}</MenuItem>)}
                        </Select>
                      )}
                    </TableCell>
                    <TableCell>
                      {addSensitivity === 'PROTECTED' && !isAdminType && (
                        <Select
                          size="small"
                          value={addDomain}
                          onChange={(e) => setAddDomain(e.target.value)}
                          displayEmpty
                          sx={{ fontSize: 12, width: '100%' }}
                          data-testid="domain"
                        >
                          <MenuItem value="" sx={{ fontSize: 12 }}>Select domain…</MenuItem>
                          {availableDomains.map((d) => <MenuItem key={d} value={d} sx={{ fontSize: 12 }}>{d}</MenuItem>)}
                        </Select>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        size="small"
                        onClick={handleAdd}
                        disabled={!canAdd}
                        data-testid="add-permission"
                        sx={{ fontSize: 11, whiteSpace: 'nowrap' }}
                      >
                        + Add
                      </Button>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {addError && (
            <Typography sx={{ px: 2, py: 1, fontSize: 12, color: 'error.main' }}>{addError}</Typography>
          )}
        </FormCard>
      </form>

      <Box sx={{ mt: 3 }}>
        <FormCard
          title={<Box component="span" sx={{ color: 'error.main' }}>Delete User</Box>}
          actionsError={deleteError}
          actions={
            <>
              <Button variant="contained" color="error" disabled={isDeleting} onClick={() => doDelete()}>
                {isDeleting ? 'Deleting…' : 'Delete subject'}
              </Button>
              <Button variant="outlined" component={Link} href="/subject">
                Cancel
              </Button>
            </>
          }
        >
          <Alert severity="error" variant="outlined" sx={{ mb: 0 }}>
            Permanently delete <strong>{name as string}</strong> and all their permissions. This <strong>cannot be undone</strong>.
          </Alert>
        </FormCard>
      </Box>
    </Box>
  )
}

function removePermOption(permission: PermissionType, permsList: Record<string, unknown>) {
  if (!permsList) return permsList
  const { type, layer, sensitivity, domain } = permission as {
    type: string; layer?: string; sensitivity?: string; domain?: string
  }
  const typeList = permsList[type] as Record<string, unknown>

  if (!layer) {
    delete permsList[type]
    return permsList
  }

  const layerList = typeList?.[layer] as Record<string, unknown>
  if (!sensitivity) return permsList
  const sensitivityList = layerList?.[sensitivity] as Record<string, unknown>

  if (domain) {
    if (sensitivityList && domain in sensitivityList) delete sensitivityList[domain]
    if (sensitivityList && !Object.keys(sensitivityList).length) delete layerList[sensitivity]
    if (layerList && !Object.keys(layerList).length) delete typeList[layer]
  } else {
    if (layerList && sensitivity in layerList) delete layerList[sensitivity]
    if (layerList && (!Object.keys(layerList).length || sensitivity === 'ALL')) {
      delete typeList[layer]
      if (typeList && (!Object.keys(typeList).length || layer === 'ALL')) delete permsList[type]
    }
  }

  return permsList
}

export default SubjectModifyPage

SubjectModifyPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Modify Subject">{page}</AccountLayout>
)
