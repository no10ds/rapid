import { Select } from '@mui/material'
import { ComponentProps } from 'react'

type SelectProps =
  | {
      checkboxes?: never
    }
  | {
      checkboxes: true
    }

export type Props = {
  fullWidth?: boolean
  data?: string[]
  // error?: string
  helperText?: string
} & SelectProps &
  ComponentProps<typeof Select>

export type CheckBoxValue = string[]
