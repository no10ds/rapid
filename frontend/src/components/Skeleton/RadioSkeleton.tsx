import { Box, styled } from '@mui/material'
import React, { ComponentProps, FC } from 'react'
import Skeleton from '@/components/Skeleton/Skeleton'

type Props = ComponentProps<typeof Box>

const Wrapper = styled(Box)`
  display: flex;
  gap: 12px;
`

const RadioSkeleton: FC<Props> = (props) => (
  <Wrapper {...props}>
    <Skeleton animation="wave" height={30} width={20} />
    <Skeleton animation="wave" height={30} width="100%" />
  </Wrapper>
)

export default RadioSkeleton
