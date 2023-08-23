import { TableCellProps } from '@mui/material'

export const asVerticalTableList = (
  list: {
    name: string
    value: string
  }[]
) => [
  ...list.map<TableCellProps[]>(({ name, value }) => [
    { children: name, component: 'th' },
    { children: value }
  ])
]
