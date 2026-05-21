import Link from 'next/link'
import { Button, Typography } from '@mui/material'
import { CenteredGradientPage } from '@/components'

function FourOhFour() {
  return (
    <CenteredGradientPage>
      <Typography variant="h1" sx={{ fontSize: 22, mb: 2 }}>
        Oops — Page not found
      </Typography>
      <Button component={Link} href="/" variant="contained" fullWidth>
        Go Home
      </Button>
    </CenteredGradientPage>
  )
}

export default FourOhFour
