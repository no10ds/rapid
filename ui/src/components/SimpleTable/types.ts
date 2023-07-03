import { Table, TableCell } from '@mui/material'
import { ComponentProps, ReactNode } from 'react'

export type DataRow = ComponentProps<typeof TableCell>

export type Props = {
  loading?: boolean
  headers?: DataRow[]
  list: DataRow[][]
  children?: ReactNode
  noRowContent?: string
} & ComponentProps<typeof Table>
