import {
  Checkbox,
  ListItemText,
  MenuItem,
  Select as MuiSelect,
  SelectChangeEvent
} from '@mui/material'
import { FC, forwardRef, ReactNode, useState } from 'react'
import { CheckBoxValue, Props } from './types'

const ITEM_HEIGHT = 86
const ITEM_PADDING_TOP = 8

const SelectCheckbox: FC<Props> = forwardRef<FC, Props>(
  ({ data = [], onChange, defaultValue = [], ...props }, ref) => {
    const [selectValue, setSelectValue] = useState<CheckBoxValue>(
      defaultValue as CheckBoxValue
    )

    const handleChange = (
      event: SelectChangeEvent<typeof selectValue>,
      child: ReactNode
    ) => {
      const {
        target: { value }
      } = event
      setSelectValue(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value
      )
      if (typeof onChange === 'function') onChange(event, child)
    }

    return (
      <MuiSelect
        sx={{
          backgroundColor: '#fff'
        }}
        {...props}
        value={selectValue}
        multiple
        renderValue={(selected: CheckBoxValue) => selected.join(', ')}
        onChange={handleChange}
        MenuProps={{
          PaperProps: {
            style: {
              maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
              width: 250
            }
          }
        }}
        ref={ref}
      >
        {data.map((label) => (
          <MenuItem key={label} value={label}>
            <Checkbox checked={selectValue.indexOf(label) > -1} />
            <ListItemText primary={label} disableTypography />
          </MenuItem>
        ))}
      </MuiSelect>
    )
  }
)

SelectCheckbox.displayName = 'SelectCheckbox'

export default SelectCheckbox
