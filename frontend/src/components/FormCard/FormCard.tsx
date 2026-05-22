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
    <Paper variant="outlined" sx={{ borderRadius: '8px', overflow: 'hidden' }}>
      <Box
        sx={{
          px: '20px',
          py: '14px',
          bgcolor: '#fafafa',
          borderBottom: '1px solid #f3f4f6',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}
      >
        {num !== undefined && (
          <Box
            sx={{
              width: 22,
              height: 22,
              borderRadius: '50%',
              bgcolor: 'primary.main',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 10,
              fontWeight: 700,
              boxShadow: '0 1px 3px rgba(236, 72, 153, 0.3)',
              flexShrink: 0
            }}
          >
            {num}
          </Box>
        )}
        <Typography sx={{ fontSize: 13, fontWeight: 600, color: 'text.primary', letterSpacing: '-0.01em' }}>
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
      <Box sx={{ p: '20px', ...bodySx }}>{children}</Box>
      {actions && (
        <Box
          sx={{
            px: '20px',
            py: '14px',
            borderTop: '1px solid #f3f4f6',
            display: 'flex',
            gap: '10px',
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
