import { Card as MuiCard, styled, CardContent, CardActions } from '@mui/material'
import { ComponentProps, ReactNode } from 'react'

type Props = {
  children: ReactNode
  action?: ReactNode
} & ComponentProps<typeof MuiCard>

const StyledCard = styled(MuiCard)`
  width: 100%;
  .MuiCardActions-root {
    padding: 0 ${(p) => p.theme.spacing(3)} ${(p) => p.theme.spacing(3)};
  }
`

const Card = ({ children, action, ...props }: Props) => {
  return (
    <StyledCard {...props}>
      <CardContent>{children}</CardContent>
      {action && <CardActions>{action}</CardActions>}
    </StyledCard>
  )
}

export default Card
