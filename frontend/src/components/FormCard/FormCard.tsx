import { Alert, Box, Paper, Typography } from '@mui/material'
import { ReactNode } from 'react'

type Props = {
  num?: number
  title: ReactNode
  optional?: boolean
  headerAction?: ReactNode
  actions?: ReactNode
  actionsError?: Error | null
  children: ReactNode
  bodySx?: object
}

const FormCard = ({
  num,
  title,
  optional,
  headerAction,
  actions,
  actionsError,
  children,
  bodySx
}: Props) => {
  return (
    <Paper variant="outlined">
      <Box
        sx={{
          p: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          gap: 1.5
        }}
      >
        {num !== undefined && (
          <Box
            sx={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 12,
              fontWeight: 600
            }}
          >
            {num}
          </Box>
        )}
        <Typography variant="h3" sx={{ fontSize: 14 }}>
          {title}
          {optional && (
            <Typography
              component="span"
              sx={{ fontWeight: 400, fontSize: 12, color: 'text.disabled', ml: 0.5 }}
            >
              (optional)
            </Typography>
          )}
        </Typography>
        {headerAction && <Box sx={{ ml: 'auto' }}>{headerAction}</Box>}
      </Box>
      <Box sx={{ p: 2, ...bodySx }}>{children}</Box>
      {actions && (
        <Box
          sx={{
            p: 2,
            borderTop: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            gap: 1,
            alignItems: 'center',
            flexWrap: 'wrap'
          }}
        >
          {actions}
          {actionsError && (
            <Alert severity="error" variant="outlined" sx={{ ml: 1, py: 0 }}>
              {actionsError.message}
            </Alert>
          )}
        </Box>
      )}
    </Paper>
  )
}

export default FormCard
