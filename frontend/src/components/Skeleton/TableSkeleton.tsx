import { Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material'
import React, { ComponentProps, FC } from 'react'
import Skeleton from '@/components/Skeleton/Skeleton'

type Props = {
  rows?: number
  columns?: number
} & ComponentProps<typeof Table>

const min = 60
const max = 70

const TableSkeleton: FC<Props> = ({ rows = 4, columns = 5, ...props }) => (
  <Table {...props}>
    <TableHead>
      <TableRow>
        {[...Array(columns).keys()].map((i) => (
          <TableCell key={i} sx={{ textAlign: 'center' }}>
            <Skeleton animation="wave" sx={{ maxWidth: '20%' }} />
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
    <TableBody>
      {[...Array(rows).keys()].map((i) => (
        <TableRow key={i}>
          {[...Array(columns).keys()].map((i) => (
            <TableCell key={i}>
              <Skeleton
                sx={{ maxWidth: `${Math.floor(Math.random() * (max - min) + min)}%` }}
              />
            </TableCell>
          ))}
        </TableRow>
      ))}
    </TableBody>
  </Table>
)

export default TableSkeleton
