import { Skeleton as MuiSkeleton } from '@mui/material'
import { styled } from '@mui/material/styles'
import { ComponentProps } from 'react'

type Props = ComponentProps<typeof MuiSkeleton>

const StyledSkeleton = styled(MuiSkeleton)`
  border-radius: 0;
`

const Skeleton = (props: Props) => (
  <StyledSkeleton height={30} animation="wave" {...props} />
)

export default Skeleton
