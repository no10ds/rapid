import {
  Avatar,
  Box,
  Divider,
  Drawer as MuiDrawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography
} from '@mui/material'
import { styled } from '@mui/material/styles'
import { ComponentProps } from 'react'
import { Logo } from '@/components/Icon'
import { Icon } from '@/components/Icon/types'
import * as Icons from '@/components/Icon'
import { useRouter } from 'next/router'
import Link from 'next/link'

type List = {
  text: string
  href?: string
  divider?: boolean
  icon?: Icon
}

type Props = {
  list: List[]
  username?: string
} & ComponentProps<typeof MuiDrawer>

const MenuBar = styled(MuiDrawer)`
  .logo {
    font-size: 105px;
    position: absolute;
  }

  a {
    color: inherit;
  }
`

export default function Drawer({ list, username, ...props }: Props) {
  const router = useRouter()
  const { asPath } = router

  const displayName = username || 'User'
  const initials = displayName.charAt(0).toUpperCase()

  return (
    <MenuBar
      variant="permanent"
      sx={{
        '& .MuiDrawer-paper': {
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column'
        }
      }}
      {...props}
    >
      <Link href="/">
        <Toolbar variant="dense">
          <Logo className="logo" />
        </Toolbar>
      </Link>
      <Divider />
      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
        {list.map(({ text, divider, icon, href }) => {
          const Icon = Icons[icon]
          return (
            <List key={text}>
              <ListItem
                dense
                component={!!href ? 'a' : 'div'}
                href={href || undefined}
                onClick={(e) => {
                  e.preventDefault()
                  href && router.push(href)
                }}
                sx={{ paddingTop: '1px', paddingBottom: '1px' }}
              >
                <ListItemButton
                  selected={asPath.includes(href)}
                  disabled={!icon}
                  sx={{ marginBottom: '5px' }}
                  disableRipple
                >
                  {icon && (
                    <ListItemIcon sx={{ fontSize: 22, minWidth: 40, padding: '6px 0px' }}>
                      {<Icon />}
                    </ListItemIcon>
                  )}
                  <ListItemText
                    style={{ margin: '0px 0px' }}
                    primary={
                      <Typography
                        variant="body2"
                        sx={
                          icon
                            ? { fontSize: 14, fontWeight: 500 }
                            : { fontSize: 15, color: '#000' }
                        }
                      >
                        {text}
                      </Typography>
                    }
                  />
                </ListItemButton>
              </ListItem>
              {divider && <Divider />}
            </List>
          )
        })}
      </Box>
      <Divider />
      <Box sx={{ p: 1.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 14 }}>
            {initials}
          </Avatar>
          <Typography variant="body2" sx={{ fontSize: 13, fontWeight: 500 }} noWrap>
            {displayName}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <Typography variant="body2" sx={{ fontSize: 13, px: 0.5, py: 0.25 }}>
              Home
            </Typography>
          </Link>
          <Link href="/api/docs" style={{ textDecoration: 'none', color: 'inherit' }}>
            <Typography variant="body2" sx={{ fontSize: 13, px: 0.5, py: 0.25 }}>
              Docs
            </Typography>
          </Link>
          <Link
            href="/api/oauth2/logout"
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            <Typography variant="body2" sx={{ fontSize: 13, px: 0.5, py: 0.25 }}>
              Sign Out
            </Typography>
          </Link>
        </Box>
      </Box>
    </MenuBar>
  )
}
