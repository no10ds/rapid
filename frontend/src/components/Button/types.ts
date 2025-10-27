import { ComponentProps } from 'react'
import { LoadingButton } from '@mui/lab'
import { ButtonProps } from '@mui/material'

export type Props = {
  loading?: boolean
  href?: string
  error?: string
  disableRoute?: boolean
} & ComponentProps<typeof LoadingButton>

export type ButtonOverrides = Record<string, ButtonProps>
