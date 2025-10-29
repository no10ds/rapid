import { ComponentProps, ReactNode } from 'react'
import { Link as MuiLink } from '@mui/material'
import NextLink from 'next/link'

export type Props = {
  href: string
  children: ReactNode
} & ComponentProps<typeof MuiLink>

const Link = ({ href, ...props }: Props) => (
  <NextLink href={href} passHref legacyBehavior>
    <MuiLink {...props} />
  </NextLink>
)
export default Link
