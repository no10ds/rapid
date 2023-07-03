import { Typography, styled } from '@mui/material'
import { FC } from 'react'
import { Props } from './types'

const Badge = styled(Typography)`
  background-color: ${(p) => p.theme.colors.black};
  color: ${(p) => p.theme.colors.white};
  border-radius: 50%;
  display: inline-flex;
  font-weight: bold;
  height: 24px;
  width: 24px;
  align-items: center;
  justify-content: center;
`

const BadgeNumber: FC<Props> = ({ label, ...props }) => (
  <Badge as="span" {...props}>
    {label}
  </Badge>
)

export default BadgeNumber
