import { Alert as MuiAlert, AlertTitle } from '@mui/material'
import { ComponentProps } from 'react'

type Props = { title?: string } & ComponentProps<typeof MuiAlert>

function Alert({ title, children, ...props }: Props) {
  return (
    <MuiAlert {...props}>
      {title && <AlertTitle>{title}</AlertTitle>}
      {children}
    </MuiAlert>
  )
}

export default Alert
