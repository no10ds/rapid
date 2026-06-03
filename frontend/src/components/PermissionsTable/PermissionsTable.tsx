import { Permission, ActionEnum, SensitivityEnum } from '@/service'
import { PermissionUiResponse } from '@/service/types'
import { useState } from 'react'
import { ArrayPath, FieldValues, UseFieldArrayReturn } from 'react-hook-form'
import { cloneDeep } from 'lodash'
import { z } from 'zod'
import {
  Box,
  Button,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from '@mui/material'

type ActionType = z.infer<typeof ActionEnum>
type PermissionType = z.infer<typeof Permission>
type SensitivityType = z.infer<typeof SensitivityEnum>

const PermissionsTable = <
  TFieldValues extends FieldValues,
  TName extends ArrayPath<TFieldValues>
>({
  permissionsListData,
  fieldArrayReturn,
  isModifyPage = false
}: {
  permissionsListData: PermissionUiResponse
  fieldArrayReturn: UseFieldArrayReturn<TFieldValues, TName>
  isModifyPage?: boolean
}) => {
  const { fields, append, remove } = fieldArrayReturn
  const permissionFields = fields as unknown as PermissionType[]

  const [addType, setAddType] = useState<ActionType | ''>('')
  const [addLayer, setAddLayer] = useState('')
  const [addSensitivity, setAddSensitivity] = useState<SensitivityType | ''>('')
  const [addDomain, setAddDomain] = useState('')
  const [addError, setAddError] = useState('')

  const filteredPerms = (() => {
    try {
      return permissionFields.reduce(
        (acc, perm) => removePermOption(perm, acc),
        cloneDeep(permissionsListData)
      )
    } catch (error) {
      if (!isModifyPage) throw error
      return cloneDeep(permissionsListData)
    }
  })()

  const typePerms =
    addType && filteredPerms?.[addType]
      ? (filteredPerms[addType] as Record<string, Record<string, Record<string, unknown>>>)
      : undefined
  const layerPerms = addLayer && typePerms?.[addLayer] ? typePerms[addLayer] : undefined
  const domainPerms =
    addSensitivity === 'PROTECTED' && layerPerms?.['PROTECTED']
      ? layerPerms['PROTECTED']
      : undefined

  const availableTypes = Object.keys(filteredPerms ?? {})
  const availableLayers = typePerms ? Object.keys(typePerms) : []
  const availableSensitivities = layerPerms ? Object.keys(layerPerms) : []
  const availableDomains = domainPerms ? Object.keys(domainPerms) : []

  const isAdminType = addType === 'DATA_ADMIN' || addType === 'USER_ADMIN'
  const canAdd =
    addType !== '' &&
    (isAdminType ||
      (addLayer && addSensitivity && (addSensitivity !== 'PROTECTED' || addDomain)))

  function handleAdd() {
    setAddError('')
    if (!canAdd) {
      setAddError('Please fill in all required fields.')
      return
    }
    const perm: PermissionType = isAdminType
      ? {
          type: addType as 'DATA_ADMIN' | 'USER_ADMIN',
          layer: undefined,
          sensitivity: undefined,
          domain: undefined
        }
      : {
          type: addType as 'READ' | 'WRITE',
          layer: addLayer,
          sensitivity: addSensitivity as SensitivityType,
          domain: addSensitivity === 'PROTECTED' ? addDomain : undefined
        }
    append(perm as Parameters<typeof append>[0])
    setAddType('')
    setAddLayer('')
    setAddSensitivity('')
    setAddDomain('')
  }

  const dash = <Typography component="span" sx={{ color: 'text.disabled' }}>—</Typography>

  return (
    <Box>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>Layer</TableCell>
              <TableCell>Sensitivity</TableCell>
              <TableCell>Domain</TableCell>
              <TableCell sx={{ width: 100 }} />
            </TableRow>
          </TableHead>
          <TableBody>
            {(fields as unknown as PermissionType[]).map((perm, idx) => (
              <TableRow key={idx}>
                <TableCell sx={{ fontSize: 12 }}>{perm.type}</TableCell>
                <TableCell sx={{ fontSize: 12 }}>{perm.layer ?? dash}</TableCell>
                <TableCell sx={{ fontSize: 12 }}>{perm.sensitivity ?? dash}</TableCell>
                <TableCell sx={{ fontSize: 12 }}>{perm.domain ?? dash}</TableCell>
                <TableCell>
                  <Button
                    type="button"
                    size="small"
                    color="error"
                    onClick={() => remove(idx)}
                    sx={{ fontSize: 11, minWidth: 0, p: 0 }}
                  >
                    Remove
                  </Button>
                </TableCell>
              </TableRow>
            ))}

            {availableTypes.length > 0 && (
              <TableRow sx={{ bgcolor: 'background.default' }}>
                <TableCell>
                  <Select
                    size="small"
                    fullWidth
                    native
                    value={addType}
                    onChange={(e) => {
                      setAddType(e.target.value as ActionType | '')
                      setAddLayer('')
                      setAddSensitivity('')
                      setAddDomain('')
                    }}
                    inputProps={{ 'data-testid': 'select-type' }}
                    sx={{ fontSize: 12 }}
                  >
                    <option value="">Select type…</option>
                    {availableTypes.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </Select>
                </TableCell>
                <TableCell>
                  {addType && !isAdminType && (
                    <Select
                      size="small"
                      fullWidth
                      native
                      value={addLayer}
                      onChange={(e) => {
                        setAddLayer(e.target.value as string)
                        setAddSensitivity('')
                        setAddDomain('')
                      }}
                      inputProps={{ 'data-testid': 'select-layer' }}
                      sx={{ fontSize: 12 }}
                    >
                      <option value="">Select layer…</option>
                      {availableLayers.map((l) => (
                        <option key={l} value={l}>{l}</option>
                      ))}
                    </Select>
                  )}
                </TableCell>
                <TableCell>
                  {addLayer && !isAdminType && (
                    <Select
                      size="small"
                      fullWidth
                      native
                      value={addSensitivity}
                      onChange={(e) => {
                        setAddSensitivity(e.target.value as SensitivityType | '')
                        setAddDomain('')
                      }}
                      inputProps={{ 'data-testid': 'select-sensitivity' }}
                      sx={{ fontSize: 12 }}
                    >
                      <option value="">Select sensitivity…</option>
                      {availableSensitivities.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </Select>
                  )}
                </TableCell>
                <TableCell>
                  {addSensitivity === 'PROTECTED' && !isAdminType && (
                    <Select
                      size="small"
                      fullWidth
                      native
                      value={addDomain}
                      onChange={(e) => setAddDomain(e.target.value as string)}
                      inputProps={{ 'data-testid': 'domain' }}
                      sx={{ fontSize: 12 }}
                    >
                      <option value="">Select domain…</option>
                      {availableDomains.map((d) => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </Select>
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    type="button"
                    size="small"
                    variant="contained"
                    onClick={handleAdd}
                    disabled={!canAdd}
                    data-testid="add-permission"
                    sx={{ whiteSpace: 'nowrap', fontSize: 11 }}
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
        <Typography sx={{ p: 1.5, fontSize: 12, color: 'error.main' }}>{addError}</Typography>
      )}
    </Box>
  )
}

const isEmpty = (obj: Record<string, unknown> | undefined): boolean =>
  !!obj && Object.keys(obj).length === 0

function removePermOption(
  permission: PermissionType,
  permsList: Record<string, unknown>
): Record<string, unknown> {
  if (!permsList) return permsList
  const { type, layer, sensitivity, domain } = permission as {
    type: string
    layer?: string
    sensitivity?: string
    domain?: string
  }

  // Admin perms (DATA_ADMIN / USER_ADMIN) have no layer — remove the whole type bucket.
  if (!layer) {
    delete permsList[type]
    return permsList
  }

  const typeBucket = permsList[type] as Record<string, unknown> | undefined
  const layerBucket = typeBucket?.[layer] as Record<string, unknown> | undefined

  if (!sensitivity) return permsList

  // PROTECTED perms specify a domain — remove that single domain from the sensitivity bucket.
  if (domain) {
    const sensitivityBucket = layerBucket?.[sensitivity] as
      | Record<string, unknown>
      | undefined
    if (sensitivityBucket && domain in sensitivityBucket) delete sensitivityBucket[domain]
    if (isEmpty(sensitivityBucket)) delete layerBucket?.[sensitivity]
    if (isEmpty(layerBucket)) delete typeBucket?.[layer]
    return permsList
  }

  // Non-PROTECTED perms remove the whole sensitivity. 'ALL' also collapses its parent.
  if (layerBucket && sensitivity in layerBucket) delete layerBucket[sensitivity]
  const collapseLayer = isEmpty(layerBucket) || sensitivity === 'ALL'
  if (collapseLayer) {
    delete typeBucket?.[layer]
    const collapseType = isEmpty(typeBucket) || layer === 'ALL'
    if (collapseType) delete permsList[type]
  }
  return permsList
}

export default PermissionsTable
