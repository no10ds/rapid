import { Typography } from '@mui/material'
import { ComponentProps } from 'react'

export type Props = {
  label: string
} & ComponentProps<typeof Typography>
