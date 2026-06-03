import { Alert, Box } from '@mui/material'
import { ReactNode } from 'react'

type Props = {
  error?: Error | null
  bordered?: boolean
  children: ReactNode
}

const FormActions = ({ error, bordered = true, children }: Props) => {
  return (
    <Box
      sx={{
        p: 2,
        ...(bordered && { borderTop: '1px solid', borderColor: 'divider' }),
        display: 'flex',
        gap: 1,
        alignItems: 'center',
        flexWrap: 'wrap'
      }}
    >
      {children}
      {error && (
        <Alert severity="error" variant="outlined" sx={{ ml: 1, py: 0 }}>
          {error.message}
        </Alert>
      )}
    </Box>
  )
}

export default FormActions
