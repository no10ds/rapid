import { Box, Paper } from '@mui/material'
import { ReactNode } from 'react'

const CenteredGradientPage = ({
  children,
  width = 360
}: {
  children: ReactNode
  width?: number
}) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1e3a5f 0%, #2a4a72 100%)',
        p: 2
      }}
    >
      <Paper sx={{ p: 4, width, textAlign: 'center' }}>{children}</Paper>
    </Box>
  )
}

export default CenteredGradientPage
