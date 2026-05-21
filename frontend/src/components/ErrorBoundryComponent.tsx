import Link from 'next/link'
import { Button, Typography } from '@mui/material'
import CenteredGradientPage from './CenteredGradientPage/CenteredGradientPage'

function ErrorBoundryComponent() {
  return (
    <CenteredGradientPage width={400}>
      <Typography variant="h1" sx={{ fontSize: 22, mb: 1 }}>
        Oops — Something Went Wrong
      </Typography>
      <Typography variant="body2" sx={{ fontSize: 13, mb: 3 }}>
        If this is a regular occurrence with the application please get in touch or
        raise a ticket.
      </Typography>
      <Button component={Link} href="/" variant="contained" fullWidth>
        Go Home
      </Button>
    </CenteredGradientPage>
  )
}

export default ErrorBoundryComponent
