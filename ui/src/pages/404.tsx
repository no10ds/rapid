import { Container, Box, styled, Typography } from '@mui/material'
import Link from 'next/link'

const Main = styled('main')`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;

  .main-content {
    background-color: ${(p) => p.theme.colors.dark1};
    flex-grow: 1;
    border-radius: inherit;
    box-shadow: 0px 4px 24px rgba(0, 0, 0, 0.25);
    color: ${(p) => p.theme.colors.white};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-width: 600px !important;
    height: 200px;
  }
`

function FourOhFour() {
  return (
    <Container maxWidth="lg">
      <Main>
        <Box className="main-content">
          <Typography variant="h1" gutterBottom>
            Oops - Page not found
          </Typography>
          <Typography variant="h2">
            <Link href="/" style={{ color: 'white' }}>
              Go Home
            </Link>
          </Typography>
        </Box>
      </Main>
    </Container>
  )
}

export default FourOhFour
