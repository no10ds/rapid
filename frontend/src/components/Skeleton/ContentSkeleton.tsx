import React, { FC, useMemo } from 'react'
import Skeleton from '@/components/Skeleton/Skeleton'

type Props = {
  lines?: number
}

const min = 40
const max = 70

const ContentSkeleton: FC<Props> = ({ lines = 3 }) => {
  const widths = useMemo(
    // eslint-disable-next-line react-hooks/purity
    () => [...Array(lines).keys()].map(() => Math.floor(Math.random() * (max - min) + min)),
    [lines]
  )

  return (
    <div data-testid="skeleton-content">
      {widths.map((width, i) => (
        <Skeleton key={i} sx={{ maxWidth: `${width}%` }} />
      ))}
    </div>
  )
}

export default ContentSkeleton
