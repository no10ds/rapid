import { ComponentProps, ReactNode, useState } from 'react'
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
        <Box sx={{ display: 'flex', alignItems: 'center', height: 64, pr: '10px', borderBottom: '1px solid', borderColor: 'divider', bgcolor: '#fff', flexShrink: 0, overflow: 'hidden' }}>
          <Link
            href="/"
            style={{
              flex: 1,
              minWidth: 0,
              height: '100%',
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
                objectPosition: 'center',
                padding: '8px 12px',
                height: '100%',
                width: 'auto',
                maxWidth: '100%'
              }}
              priority
            />
          </Link>
          <IconButton
            size="small"
            onClick={() => setCollapsed((c) => !c)}
            sx={{
              width: 24,
              height: 24,
              ml: 'auto',
              color: '#6b7280',
              borderRadius: 1,
              '&:hover': { bgcolor: 'rgba(0,0,0,0.08)', color: '#374151' }
            }}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRightIcon sx={{ fontSize: 14 }} /> : <ChevronLeftIcon sx={{ fontSize: 14 }} />}
          </IconButton>
        </Box>

        {/* Nav sections */}
        <Box sx={{ flex: 1, overflowY: 'auto' }}>
          {hasDataSection && (
            <Box sx={{ px: 1, pt: '12px', pb: '4px' }}>
              {!collapsed && (
                <Typography
                  sx={{ px: 1, mb: '3px', fontSize: 9, fontWeight: 600, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#9ca3af', whiteSpace: 'nowrap' }}
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
            </Box>
          )}

          {hasJobsSection && (
            <Box sx={{ px: 1, pt: '20px', pb: '4px' }}>
              {!collapsed && (
                <Typography
                  sx={{ px: 1, mb: '3px', fontSize: 9, fontWeight: 600, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#9ca3af', whiteSpace: 'nowrap' }}
                >
                  Jobs
                </Typography>
              )}
              <List disablePadding>
                <NavItem href="/tasks" icon={<WorkIcon />} label="Jobs" active={isActive(['/tasks'])} collapsed={collapsed} />
              </List>
            </Box>
          )}

          {methods?.can_manage_users && (
            <Box sx={{ px: 1, pt: '20px', pb: '4px' }}>
              {!collapsed && (
                <Typography
                  sx={{ px: 1, mb: '3px', fontSize: 9, fontWeight: 600, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#9ca3af', whiteSpace: 'nowrap' }}
                >
                  Admin
                </Typography>
              )}
              <List disablePadding>
                <NavItem href="/subject" icon={<PeopleIcon />} label="User Admin" active={isActive(['/subject'])} collapsed={collapsed} />
              </List>
            </Box>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{ borderTop: '1px solid', borderColor: 'secondary.light', px: 1, py: '10px' }}>
          {!collapsed && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: '2px', px: '4px', pb: '6px' }}>
              {[
                { label: 'Docs', href: 'https://rapid.readthedocs.io/en/latest/' },
                { label: 'API Docs', href: '/api/docs' },
                { label: 'Source Code', href: 'https://github.com/no10ds/rapid' }
              ].map((link) => (
                <Typography
                  key={link.label}
                  component="a"
                  href={link.href}
                  target={link.href.startsWith('http') ? '_blank' : undefined}
                  rel={link.href.startsWith('http') ? 'noreferrer' : undefined}
                  sx={{
                    display: 'block',
                    fontSize: 13,
                    fontWeight: 500,
                    color: '#e5e7eb',
                    textDecoration: 'none',
                    px: '8px',
                    py: '6px',
                    borderRadius: '5px',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.04)', color: '#fff' }
                  }}
                >
                  {link.label}
                </Typography>
              ))}
            </Box>
          )}
          <Box
            sx={{
              height: 36,
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              px: '6px',
              cursor: 'pointer',
              borderRadius: '5px',
              '&:hover': { bgcolor: 'rgba(255,255,255,0.04)' }
            }}
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main', fontSize: 9, fontWeight: 700, letterSpacing: '0.02em' }}>
              {initials ?? '?'}
            </Avatar>
            {!collapsed && (
              <Box sx={{ minWidth: 0 }}>
                {username && <Typography sx={{ fontSize: 12, color: '#d1d5db', fontWeight: 500, lineHeight: 1.2 }} noWrap>{username}</Typography>}
                <Typography sx={{ fontSize: 10, color: '#9ca3af', fontWeight: 400, lineHeight: 1.2 }}>
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
        <Box sx={{ height: 64, display: 'flex', alignItems: 'center', gap: 1.5, px: '28px', borderBottom: '1px solid', borderColor: 'divider', bgcolor: '#fff', flexShrink: 0 }}>
          <Typography sx={{ fontSize: 16, fontWeight: 600, color: 'text.primary', letterSpacing: '-0.01em' }}>
            {title}
          </Typography>
          <Box sx={{ flex: 1 }} />
          {topbarActions}
        </Box>

        {/* Content */}
        <Box sx={{ flex: 1, overflowY: 'auto', p: noPad ? 0 : '28px', bgcolor: 'background.default' }}>
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
        position: 'relative',
        height: 38,
        mb: '2px',
        px: '10px',
        gap: '10px',
        borderRadius: '5px',
        justifyContent: collapsed ? 'center' : 'flex-start',
        color: active ? '#fff' : '#e5e7eb',
        '&:hover': { bgcolor: 'rgba(255,255,255,0.04)' },
        '&.Mui-selected': {
          bgcolor: 'rgba(236, 72, 153, 0.1)',
          '&:hover': { bgcolor: 'rgba(236, 72, 153, 0.15)' }
        },
        '&.Mui-selected::before': {
          content: '""',
          position: 'absolute',
          left: 0,
          top: 6,
          bottom: 6,
          width: 2,
          bgcolor: 'primary.main',
          borderRadius: '0 2px 2px 0'
        }
      }}
    >
      <ListItemIcon sx={{ minWidth: 22, width: 22, height: 22, color: active ? 'primary.main' : '#d1d5db', '& .MuiSvgIcon-root': { fontSize: 19 } }}>
        {icon}
      </ListItemIcon>
      {!collapsed && (
        <ListItemText
          primary={label}
          primaryTypographyProps={{
            fontSize: 13,
            fontWeight: active ? 500 : 400,
            color: active ? '#fff' : '#e5e7eb',
            letterSpacing: '0.01em'
          }}
        />
      )}
    </ListItemButton>
  )
}

export default AccountLayout
