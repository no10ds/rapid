import { ComponentProps, ReactNode, useState, useRef, useEffect } from 'react'
import { useQueries } from '@tanstack/react-query'
import { getAuthStatus, getMethods } from '@/service'
import { MethodsResponse } from '@/service/types'
import { useRouter } from 'next/router'
import Router from 'next/router'
import Link from 'next/link'
import Image from 'next/image'
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress,
  Divider
} from '@mui/material'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import SearchIcon from '@mui/icons-material/Search'
import TableChartIcon from '@mui/icons-material/TableChart'
import WorkIcon from '@mui/icons-material/Work'
import PeopleIcon from '@mui/icons-material/People'
import AddBoxIcon from '@mui/icons-material/AddBox'

const SIDEBAR_WIDTH = 240
const SIDEBAR_COLLAPSED = 60

type AccountLayoutProps = {
  title?: string
  topbarActions?: ReactNode
  noPad?: boolean
  children: ReactNode
} & Omit<ComponentProps<'div'>, 'children' | 'title'>

const AccountLayout = ({ children, title, topbarActions, noPad }: AccountLayoutProps) => {
  const [collapsed, setCollapsed] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const router = useRouter()

  const redirect = () => {
    Router.replace({ pathname: '/login' })
  }

  const results = useQueries({
    queries: [
      {
        queryKey: ['authStatus'],
        queryFn: getAuthStatus,
        keepPreviousData: true,
        staleTime: Infinity,
        refetchOnWindowFocus: false,
        onError: () => redirect(),
        onSuccess: (data: { detail: string }) => {
          if (data.detail === 'fail') redirect()
        }
      },
      {
        queryKey: ['methods'],
        queryFn: getMethods,
        keepPreviousData: true,
        staleTime: Infinity,
        refetchOnWindowFocus: false
      }
    ]
  })

  const methods: MethodsResponse | undefined = results[1].data

  if (results[0].isLoading) {
    return <LinearProgress color="primary" role="progressbar" aria-label="Loading" />
  }

  const sidebarWidth = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_WIDTH
  const username = methods?.username ?? null
  const initials = username ? username.slice(0, 2).toUpperCase() : null

  const hasDataSection =
    methods?.can_upload ||
    methods?.can_download ||
    methods?.can_search_catalog ||
    methods?.can_create_schema

  const hasJobsSection = methods?.can_upload || methods?.can_download

  function isActive(paths: string[]) {
    return paths.some((p) => {
      if (p === '/') return router.asPath === '/'
      return router.asPath.startsWith(p)
    })
  }

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: sidebarWidth,
          flexShrink: 0,
          transition: 'width 0.2s',
          '& .MuiDrawer-paper': {
            width: sidebarWidth,
            transition: 'width 0.2s',
            bgcolor: 'secondary.main',
            borderRight: '1px solid',
            borderColor: 'secondary.light',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }
        }}
      >
        {/* Logo + collapse toggle */}
        <Box sx={{ display: 'flex', alignItems: 'center', height: 56, px: 1 }}>
          <Link
            href="/"
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              overflow: 'hidden'
            }}
          >
            <Image
              src="/img/logo.png"
              alt="rAPId"
              width={160}
              height={40}
              style={{
                objectFit: 'contain',
                height: '32px',
                width: 'auto',
                maxWidth: '100%'
              }}
              priority
            />
          </Link>
          <IconButton
            size="small"
            onClick={() => setCollapsed((c) => !c)}
            sx={{ color: 'rgba(255,255,255,0.6)', '&:hover': { color: '#fff' } }}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRightIcon fontSize="small" /> : <ChevronLeftIcon fontSize="small" />}
          </IconButton>
        </Box>

        {/* Nav sections */}
        <Box sx={{ flex: 1, overflowY: 'auto', px: 1, mt: 1 }}>
          {hasDataSection && (
            <>
              {!collapsed && (
                <Typography
                  variant="body2"
                  sx={{ px: 1.5, py: 0.5, fontSize: 10, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.4)' }}
                >
                  Data
                </Typography>
              )}
              <List disablePadding>
                {methods?.can_search_catalog && (
                  <NavItem href="/catalog" icon={<SearchIcon />} label="Catalog" active={isActive(['/catalog'])} collapsed={collapsed} />
                )}
                {methods?.can_create_schema && (
                  <NavItem href="/schema/create" icon={<AddBoxIcon />} label="Add Dataset" active={isActive(['/schema/create'])} collapsed={collapsed} />
                )}
              </List>
            </>
          )}

          {hasJobsSection && (
            <>
              {!collapsed && (
                <Typography
                  variant="body2"
                  sx={{ px: 1.5, py: 0.5, mt: 2, fontSize: 10, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.4)' }}
                >
                  Jobs
                </Typography>
              )}
              <List disablePadding>
                <NavItem href="/tasks" icon={<WorkIcon />} label="Jobs" active={isActive(['/tasks'])} collapsed={collapsed} />
              </List>
            </>
          )}

          {methods?.can_manage_users && (
            <>
              {!collapsed && (
                <Typography
                  variant="body2"
                  sx={{ px: 1.5, py: 0.5, mt: 2, fontSize: 10, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.4)' }}
                >
                  Admin
                </Typography>
              )}
              <List disablePadding>
                <NavItem href="/subject" icon={<PeopleIcon />} label="User Admin" active={isActive(['/subject'])} collapsed={collapsed} />
              </List>
            </>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{ borderTop: '1px solid', borderColor: 'secondary.light', p: 1 }}>
          {!collapsed && (
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', px: 1, py: 0.5, mb: 1 }}>
              {[
                { label: 'Docs', href: 'https://rapid.readthedocs.io/en/latest/' },
                { label: 'API', href: '/api/docs' },
                { label: 'Source', href: 'https://github.com/no10ds/rapid' }
              ].map((link) => (
                <Typography
                  key={link.label}
                  component="a"
                  href={link.href}
                  target={link.href.startsWith('http') ? '_blank' : undefined}
                  rel={link.href.startsWith('http') ? 'noreferrer' : undefined}
                  sx={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', textDecoration: 'none', '&:hover': { color: '#fff' } }}
                >
                  {link.label}
                </Typography>
              ))}
            </Box>
          )}
          <Box
            sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 1, py: 0.5, cursor: 'pointer', borderRadius: 1, '&:hover': { bgcolor: 'rgba(255,255,255,0.04)' } }}
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            <Avatar sx={{ width: 28, height: 28, bgcolor: 'primary.main', fontSize: 11 }}>
              {initials ?? '?'}
            </Avatar>
            {!collapsed && (
              <Box sx={{ minWidth: 0 }}>
                {username && <Typography sx={{ fontSize: 12, color: '#fff', fontWeight: 500, lineHeight: 1.2 }} noWrap>{username}</Typography>}
                <Typography sx={{ fontSize: 10, color: 'rgba(255,255,255,0.5)', lineHeight: 1.2 }}>
                  {methods?.can_manage_users ? 'User Admin' : 'Data User'}
                </Typography>
              </Box>
            )}
          </Box>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            transformOrigin={{ vertical: 'bottom', horizontal: 'left' }}
          >
            <MenuItem component="a" href="/api/oauth2/logout" sx={{ fontSize: 13 }}>
              Sign out
            </MenuItem>
          </Menu>
        </Box>
      </Drawer>

      {/* Main content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Topbar */}
        <Box sx={{ height: 52, display: 'flex', alignItems: 'center', px: 3, borderBottom: '1px solid', borderColor: 'divider', bgcolor: '#fff', flexShrink: 0 }}>
          <Typography variant="h3" sx={{ fontSize: 15, fontWeight: 600, letterSpacing: '-0.3px' }}>
            {title}
          </Typography>
          <Box sx={{ flex: 1 }} />
          {topbarActions}
        </Box>

        {/* Content */}
        <Box sx={{ flex: 1, overflowY: 'auto', p: noPad ? 0 : 3.5, bgcolor: 'background.default' }}>
          {children}
        </Box>
      </Box>
    </Box>
  )
}

function NavItem({ href, icon, label, active, collapsed }: { href: string; icon: ReactNode; label: string; active: boolean; collapsed: boolean }) {
  return (
    <ListItemButton
      component={Link}
      href={href}
      selected={active}
      sx={{
        mb: 0.5,
        minHeight: 36,
        px: collapsed ? 1.5 : 2,
        justifyContent: collapsed ? 'center' : 'flex-start',
        color: active ? '#fff' : 'rgba(255,255,255,0.7)',
        '&:hover': { bgcolor: 'rgba(255,255,255,0.06)', color: '#fff' },
        '&.Mui-selected': { bgcolor: 'rgba(255,255,255,0.1)', color: '#fff' }
      }}
    >
      <ListItemIcon sx={{ minWidth: collapsed ? 0 : 32, color: 'inherit', '& .MuiSvgIcon-root': { fontSize: 18 } }}>
        {icon}
      </ListItemIcon>
      {!collapsed && <ListItemText primary={label} primaryTypographyProps={{ fontSize: 13, fontWeight: active ? 600 : 400 }} />}
    </ListItemButton>
  )
}

export default AccountLayout
