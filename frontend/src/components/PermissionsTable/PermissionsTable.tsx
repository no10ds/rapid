import { Permission, ActionEnum, SensitivityEnum } from '@/service'
import { PermissionUiResponse } from '@/service/types'
import { useState } from 'react'
import { FieldValues } from 'react-hook-form'
import { cloneDeep } from 'lodash'
import { z } from 'zod'

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

  return (
    <div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #f0f0f0' }}>
            <th style={thStyle}>Type</th>
            <th style={thStyle}>Layer</th>
            <th style={thStyle}>Sensitivity</th>
            <th style={thStyle}>Domain</th>
            <th style={{ ...thStyle, width: 80 }}></th>
          </tr>
        </thead>
        <tbody>
          {(fields as unknown as PermissionType[]).map((perm, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid #f9f9f9' }}>
              <td style={tdStyle}>{perm.type}</td>
              <td style={tdStyle}>
                {perm.layer ?? <span style={{ color: 'var(--text-tertiary)' }}>—</span>}
              </td>
              <td style={tdStyle}>
                {perm.sensitivity ?? <span style={{ color: 'var(--text-tertiary)' }}>—</span>}
              </td>
              <td style={tdStyle}>
                {perm.domain ?? <span style={{ color: 'var(--text-tertiary)' }}>—</span>}
              </td>
              <td style={tdStyle}>
                <button
                  type="button"
                  onClick={() => remove(idx)}
                  style={{
                    fontSize: 11,
                    color: '#dc2626',
                    fontWeight: 500,
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 0
                  }}
                >
                  Remove
                </button>
              </td>
            </tr>
          ))}

          {availableTypes.length > 0 && (
            <tr style={{ background: '#f9fafb', borderTop: '2px dashed #e5e7eb' }}>
              <td style={tdStyle}>
                <select
                  className="f-sel"
                  style={{ height: 30, fontSize: 12, width: '100%' }}
                  value={addType}
                  onChange={(e) => {
                    setAddType(e.target.value as ActionType | '')
                    setAddLayer('')
                    setAddSensitivity('')
                    setAddDomain('')
                  }}
                  data-testid="select-type"
                >
                  <option value="">Select type…</option>
                  {availableTypes.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </td>
              <td style={tdStyle}>
                {addType && !isAdminType && (
                  <select
                    className="f-sel"
                    style={{ height: 30, fontSize: 12, width: '100%' }}
                    value={addLayer}
                    onChange={(e) => {
                      setAddLayer(e.target.value)
                      setAddSensitivity('')
                      setAddDomain('')
                    }}
                    data-testid="select-layer"
                  >
                    <option value="">Select layer…</option>
                    {availableLayers.map((l) => (
                      <option key={l} value={l}>
                        {l}
                      </option>
                    ))}
                  </select>
                )}
              </td>
              <td style={tdStyle}>
                {addLayer && !isAdminType && (
                  <select
                    className="f-sel"
                    style={{ height: 30, fontSize: 12, width: '100%' }}
                    value={addSensitivity}
                    onChange={(e) => {
                      setAddSensitivity(e.target.value as SensitivityType | '')
                      setAddDomain('')
                    }}
                    data-testid="select-sensitivity"
                  >
                    <option value="">Select sensitivity…</option>
                    {availableSensitivities.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                )}
              </td>
              <td style={tdStyle}>
                {addSensitivity === 'PROTECTED' && !isAdminType && (
                  <select
                    className="f-sel"
                    style={{ height: 30, fontSize: 12, width: '100%' }}
                    value={addDomain}
                    onChange={(e) => setAddDomain(e.target.value)}
                    data-testid="domain"
                  >
                    <option value="">Select domain…</option>
                    {availableDomains.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                )}
              </td>
              <td style={tdStyle}>
                <button
                  type="button"
                  className="btn-primary"
                  style={{ height: 30, fontSize: 11, whiteSpace: 'nowrap' }}
                  onClick={handleAdd}
                  data-testid="add-permission"
                  disabled={!canAdd}
                >
                  + Add
                </button>
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {addError && (
        <div style={{ padding: '8px 16px', fontSize: 12, color: '#dc2626' }}>{addError}</div>
      )}
    </div>
  )
}

const thStyle: React.CSSProperties = {
  padding: '7px 12px',
  fontSize: 10,
  fontWeight: 600,
  letterSpacing: '.06em',
  textTransform: 'uppercase',
  color: '#71717a',
  textAlign: 'left'
}

const tdStyle: React.CSSProperties = {
  padding: '8px 12px',
  fontSize: 12
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
