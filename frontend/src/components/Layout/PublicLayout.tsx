import { Box, Container, styled, Typography } from '@mui/material'
import { Logo, GovLogo } from '@/components/Icon'
import { ComponentProps, ReactNode } from 'react'

type Props = { promo?: ReactNode; title: string } & ComponentProps<typeof Box>

const overlap = 50

const Main = styled('main')`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;

  .columns {
    display: flex;
    box-shadow: 0px 4px 4px rgb(0 0 0 / 25%);
    background-color: ${(p) => p.theme.colors.white};
    min-height: 540px;
  }

  .promo,
  .main-content {
    padding: ${(p) => p.theme.spacing(4)};
  }

  .header {
    height: 60px;
    display: flex;
    align-items: center;
    margin-bottom: ${(p) => p.theme.spacing(3)};
    svg {
      font-size: 50px;
    }
  }

  .promo {
    color: ${(p) => p.theme.colors.black};
    padding-right: calc(${(p) => p.theme.spacing(4)} + ${overlap}px);
    flex-basis: 70%;
    position: relative;
    svg {
      color: ${(p) => p.theme.colors.black};
    }
  }

  .main-content {
    background-color: ${(p) => p.theme.colors.dark1};
    flex-grow: 1;
    border-radius: inherit;
    box-shadow: 0px 4px 24px rgba(0, 0, 0, 0.25);
    margin: -3px 0px -3px -${overlap}px;
    color: ${(p) => p.theme.colors.white};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .logo {
    position: absolute;
    bottom: 0px;
    right: 20px;
    font-size: 120px;
  }

  .space-icon {
    font-size: 473px;
    position: absolute;
    right: -103px;
    bottom: -143px;
    z-index: 1;
    opacity: 0.9;
    pointer-events: none;
  }
  .content {
    z-index: 2;
    position: relative;
  }
`

const PublicLayout = ({ children, promo, title, ...props }: Props) => (
  <Container maxWidth="lg">
    <Main>
      <Box className="columns" {...props}>
        {promo && (
          <div className="promo">
            <div className="header">
              <GovLogo />
            </div>
            <div className="content">{promo}</div>
          </div>
        )}
        <Box className="main-content">
          {title && (
            <div className="header">
              <Typography variant="h1">{title}</Typography>
            </div>
          )}
          {children}
        </Box>
        <Logo className="logo" />
      </Box>
    </Main>
  </Container>
)

export default PublicLayout
