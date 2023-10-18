import { Dialog as MuiDialog, DialogTitle as MuiDialogTitle } from '@mui/material'
import { ComponentProps } from 'react'

type Props = {
  open: boolean
  title?: string
} & ComponentProps<typeof MuiDialog>

function Dialog({ open, title, children, ...props }: Props) {
  return (
    <MuiDialog open={open} {...props}>
      {title && <MuiDialogTitle>{title}</MuiDialogTitle>}
      {children}
    </MuiDialog>
  )
}

export default Dialog
