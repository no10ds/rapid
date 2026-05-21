import { Permission, ActionEnum, SensitivityEnum } from '@/service'
import { PermissionUiResponse } from '@/service/types'
import { useState } from 'react'
import { FieldValues } from 'react-hook-form'
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

const PermissionsTable = ({
  permissionsListData,
  fieldArrayReturn,
  isModifyPage = false
}: {
  permissionsListData: PermissionUiResponse
  fieldArrayReturn: FieldValues
  isModifyPage?: boolean
}) => {
  const { fields, append, remove } = fieldArrayReturn

  const [addType, setAddType] = useState<ActionType | ''>('')
  const [addLayer, setAddLayer] = useState('')
  const [addSensitivity, setAddSensitivity] = useState<SensitivityType | ''>('')
  const [addDomain, setAddDomain] = useState('')
  const [addError, setAddError] = useState('')

  let filteredPerms = cloneDeep(permissionsListData)
  try {
    ;(fields as unknown as PermissionType[]).forEach((perm) => {
      filteredPerms = removePermOption(perm, filteredPerms)
    })
  } catch (error) {
    if (!isModifyPage) throw error
  }

  const availableTypes = Object.keys(filteredPerms ?? {})
  const availableLayers =
    addType && filteredPerms?.[addType] ? Object.keys(filteredPerms[addType] as object) : []
  const availableSensitivities =
    addType && addLayer && (filteredPerms?.[addType] as Record<string, unknown>)?.[addLayer]
      ? Object.keys(
          (filteredPerms[addType] as Record<string, Record<string, unknown>>)[addLayer]
        )
      : []
  const availableDomains =
    addType &&
    addLayer &&
    addSensitivity === 'PROTECTED' &&
    (
      filteredPerms?.[addType] as Record<string, Record<string, Record<string, unknown>>>
    )?.[addLayer]?.['PROTECTED']
      ? Object.keys(
          (
            filteredPerms[addType] as Record<string, Record<string, Record<string, unknown>>>
          )[addLayer]['PROTECTED']
        )
      : []

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
    append(perm)
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

export default PermissionsTable
