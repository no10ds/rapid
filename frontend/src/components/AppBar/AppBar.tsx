import * as React from 'react'
import {
  IconButton,
  Typography,
  Toolbar,
  AppBar as MuiAppBar,
  Menu,
  styled
} from '@mui/material'
import AccountCircle from '@mui/icons-material/AccountCircle'
import MenuItem from '@mui/material/MenuItem'
import { ComponentProps } from 'react'
import Link from '../Link'
import { useRouter } from 'next/router'

type Props = { title?: string } & ComponentProps<typeof MuiAppBar>

const MenuBar = styled(MuiAppBar)`
  background-color: ${(p) => p.theme.colors.dark1};
  color: ${(p) => p.theme.colors.white};
`

export default function AppBar({ title, ...props }: Props) {
  const router = useRouter()
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
    router.replace(`/api/oauth2/logout`)
  }

  return (
    <MenuBar position="fixed" {...props}>
      <Toolbar variant="dense">
        <Typography variant="body1" component="div" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>
        <Link
          color="rgb(255, 255, 255)"
          style={{ textDecoration: 'none', marginRight: '2rem' }}
          href="/"
        >
          Home
        </Link>
        <Link
          color="rgb(255, 255, 255)"
          style={{ textDecoration: 'none', marginRight: '2rem' }}
          href={`/api/docs`}
        >
          Docs
        </Link>

        <div>
          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
          <Menu
            sx={{ mt: '45px' }}
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right'
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right'
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleClose}>
              <Typography textAlign="center" variant="body2">
                Logout
              </Typography>
            </MenuItem>
          </Menu>
        </div>
      </Toolbar>
    </MenuBar>
  )
}
