import { ComponentProps, MouseEvent } from 'react'
import { Chip as MuiChip } from '@mui/material'
import { AllColors } from '@/style/types'

export type Props = {
  toggle?: boolean
  active?: boolean
  avatarText?: string
  brandColor?: AllColors

  onToggle?: (e: MouseEvent<HTMLDivElement>, active: boolean) => void
} & ComponentProps<typeof MuiChip>
