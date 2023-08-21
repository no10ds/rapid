import { Select } from '@/components'
import { zodResolver } from '@hookform/resolvers/zod'
import { Typography } from '@mui/material'
import { Controller, useForm, FieldValues } from 'react-hook-form'
import { z } from 'zod'
import { Permission, ActionEnum, SensitivityEnum } from '@/service'
import { isDataPermission } from '@/service/permissions'
import { PermissionUiResponse } from '@/service/types'
import { useEffect, useState } from 'react'
import { cloneDeep } from 'lodash'
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';


type ActionType = z.infer<typeof ActionEnum>
type PermissionType = z.infer<typeof Permission>
type SensitivityType = z.infer<typeof SensitivityEnum>


const PermissionsTable = ({ permissionsListData, fieldArrayReturn }: { permissionsListData: PermissionUiResponse, fieldArrayReturn: FieldValues }) => {

  const [filteredPermissionsListData, setFilteredPermissionsListData] = useState({})
  const [permissionsAtMax, setPermissionsAtMax] = useState<boolean>(false)

  const removePermissionAsAnOption = (permission: PermissionType, permissionsList: PermissionUiResponse) => {
    const { type, layer, sensitivity, domain } = permission;
    const typeList = permissionsList[type];
    const layerList = typeList?.[layer];
    const sensitivityList = layerList?.[sensitivity];

    switch (true) {
      // Scenario for protected permission
      case Boolean(domain):
        // Remove the domain
        if (domain in sensitivityList) {
          delete sensitivityList[domain];
        }

        // Remove the sensitivity if there are no domains left
        if (!Object.keys(sensitivityList)?.length) {
          delete layerList[sensitivity];

          // Remove the layer if there are no sensitivities left
          if (!Object.keys(layerList)?.length) {
            delete typeList[layer];
          }
        }
        break;
      case Boolean(sensitivity):
        // Remove the sensitivity
        if (sensitivity in layerList) {
          delete layerList[sensitivity];
        }

        // Remove the layer if there are no sensitivities left
        if (!Object.keys(layerList)?.length || sensitivity === "ALL") {
          delete typeList[layer];

          // Remove the type if there are no layers left
          if (!Object.keys(typeList)?.length || layer === "ALL") {
            delete permissionsList[type];
          }
        }
        break;

      // Scenario for admin permissions 
      default:
        delete permissionsList[type];
        break;
    }

    return permissionsList;
  };


  const { fields, append, remove } = fieldArrayReturn

  const { control, trigger, watch, reset, setError, setValue } = useForm<PermissionType>({
    resolver: zodResolver(Permission)
  })

  // Remove any of the selected permissions from being an option
  useEffect(() => {
    let amendedPermissions = cloneDeep(permissionsListData)
    fields.forEach((permission) => {
      amendedPermissions = removePermissionAsAnOption(permission, amendedPermissions)
    })
    setFilteredPermissionsListData(amendedPermissions)

  }, [fields, permissionsListData]);

  // Set Permissions at max
  useEffect(() => {
    if (Object.keys(filteredPermissionsListData).length === 0) {
      setPermissionsAtMax(true)
    }
    else {
      setPermissionsAtMax(false)
    }
  }, [filteredPermissionsListData])


  const generateOptions = (items) => items.map((item) => {
    return <option key={item} value={item}>{item}</option>
  })

  return (
    <TableContainer>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell></TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Layer</TableCell>
            <TableCell>Sensitivity</TableCell>
            <TableCell>Domain</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(fields || []).map((item, index) =>
          (<TableRow
            key={item.id}
            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
          >
            <TableCell
            >
              <IconButton
                color="primary"
                onClick={() => remove(index)}
              >
                <RemoveIcon />
              </IconButton>
            </TableCell>
            <TableCell>
              <Typography key={`permissions.${index}.type`}>{item.type}</Typography>
            </TableCell>
            <TableCell>
              <Typography key={`permissions.${index}.layer`}>{item.layer}</Typography>
            </TableCell>
            <TableCell>
              <Typography key={`permissions.${index}.sensitivity`}>{item.sensitivity}</Typography>
            </TableCell>
            <TableCell>
              <Typography key={`permissions.${index}.domain`}>{item.domain}</Typography>
            </TableCell>
          </TableRow>)
          )}
          {!permissionsAtMax && <TableRow>
            <TableCell>
              <IconButton
                color="primary"
                onClick={() => {
                  const result = trigger(undefined, { shouldFocus: true });
                  if (result) {
                    const permissionToAdd = watch()
                    // Triggers an error if the domain is not set for protected sensitivity
                    if (isDataPermission(permissionToAdd) && permissionToAdd.sensitivity === "PROTECTED" && permissionToAdd.domain === undefined) {
                      setError("domain", { type: "custom", message: "Required" });
                    }
                    else {
                      append(permissionToAdd)
                      reset({
                        type: undefined,
                        layer: undefined,
                        sensitivity: undefined,
                        domain: undefined,
                      })
                    }
                  }
                }}
              >
                <AddIcon />
              </IconButton>
            </TableCell>
            <TableCell>
              <Controller
                name={'type'}
                control={control}
                render={({ field, fieldState: { error } }) => (
                  <Select
                    {...field}
                    error={!!error}
                    value={field.value ? field.value : ''}
                    helperText={error?.message}
                    native
                    inputProps={{
                      'data-testid': 'select-type'
                    }}
                    // Reset all other values when this is changed
                    onChange={(event) => { reset(); setValue('type', event.target.value as ActionType) }}
                  >
                    <option value={''}>Action</option>
                    {generateOptions(Object.keys(filteredPermissionsListData))}
                  </Select>
                )}
              />
            </TableCell>
            <TableCell>
              <Controller
                name={'layer'}
                control={control}
                render={({ field, fieldState: { error } }) => (
                  isDataPermission(watch()) &&
                  <Select
                    {...field}
                    error={!!error}
                    value={field.value && isDataPermission(watch()) ? field.value : ''}
                    helperText={error?.message}
                    native
                    inputProps={{
                      'data-testid': 'select-layer'
                    }}
                  >
                    <option key={''} value={''}>Layer</option>
                    {generateOptions(Object.keys(filteredPermissionsListData[watch('type')]))}
                  </Select>
                )}
              />
            </TableCell>
            <TableCell>
              <Controller
                name={'sensitivity'}
                control={control}
                render={({ field, fieldState: { error } }) => (
                  isDataPermission(watch()) && watch('layer') &&
                  <Select
                    {...field}
                    value={field.value && isDataPermission(watch()) ? field.value : ''}
                    error={!!error}
                    helperText={error?.message}
                    native
                    inputProps={{
                      'data-testid': 'select-sensitivity'
                    }}
                    // Reset domain if this is changed
                    onChange={(event) => { setValue('domain', undefined); setValue('sensitivity', event.target.value as SensitivityType) }}
                  >
                    <option value={''}>Sensitivity</option>
                    {generateOptions(Object.keys(filteredPermissionsListData[watch('type')][watch('layer')]))}
                  </Select>
                )
                }
              />
            </TableCell>
            <TableCell>
              <Controller
                name={'domain'}
                control={control}
                render={({ field, fieldState: { error } }) => (
                  isDataPermission(watch()) && watch('sensitivity') === 'PROTECTED' &&
                  <Select
                    {...field}
                    value={field.value && isDataPermission(watch()) ? field.value : ''}
                    error={!!error}
                    helperText={error?.message}
                    native
                    inputProps={{
                      'data-testid': 'domain'
                    }}
                  >
                    <option value={''}>Domain</option>
                    {isDataPermission(watch()) && generateOptions(Object.keys(filteredPermissionsListData[watch('type')][watch('layer')][watch('sensitivity')]))}
                  </Select>)
                }
              />
            </TableCell>
          </TableRow>}
        </TableBody>
      </Table>
    </TableContainer >
  )
}

export default PermissionsTable
