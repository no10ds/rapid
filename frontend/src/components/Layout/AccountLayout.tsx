import { Box, Container, LinearProgress, styled, Toolbar } from '@mui/material'
import { ComponentProps } from 'react'
import { AppBar, Drawer } from '@/components'
import Router from 'next/router'
import { useQueries } from '@tanstack/react-query'
import { MethodsResponse } from '@/service/types'
import {
  catalogManagementMethods,
  dataDeleteMethod,
  dataDownloadMethod,
  dataUploadMethod,
  schemaManagementMethods,
  taskManagementMethods,
  userManagementMethods
} from '@/service/constants'
import { getAuthStatus, getMethods } from '@/service'

type Props = { title?: string } & ComponentProps<typeof Box>

const drawerWidth = 244

const Layout = styled(Box)`
  .columns {
    display: flex;
    width: 100%;
  }

  main {
    width: 100%;
  }

  .sidebar {
    background-color: #ccc;
    position: fixed;
    width: ${drawerWidth}px;
    top: 0;
    left: 0;
  }

  .main-content {
    margin-left: ${drawerWidth}px;
    padding: ${(p) => p.theme.spacing(3)};
    width: 100%;
  }
  .MuiDrawer-paper {
    width: ${drawerWidth}px;
  }
`

const filterSidebarList = (methods: MethodsResponse) => {
  const baseMethods = []
  if (methods) {
    if (methods.can_manage_users) baseMethods.push(...userManagementMethods)
    if (methods.can_upload || methods.can_download) {
      baseMethods.push({ text: 'Data Management' })
      if (methods.can_download) baseMethods.push(...dataDownloadMethod)
      if (methods.can_upload) {
        baseMethods.push(...dataUploadMethod)
      }
      if (methods.can_create_schema) {
        baseMethods.push(...dataDeleteMethod)
        baseMethods.push(...schemaManagementMethods)
      }
      baseMethods.push(...taskManagementMethods)
    }
    if (methods.can_search_catalog) baseMethods.push(...catalogManagementMethods)
  }

  return baseMethods
}

const AccountLayout = ({ children, title, ...props }: Props) => {
  const redirect = () => {
    Router.replace({
      pathname: '/login'
    })
  }

  const results = useQueries({
    queries: [
      {
        queryKey: ['authStatus'],
        queryFn: getAuthStatus,
        keepPreviousData: false,
        cacheTime: 0,
        refetchInterval: 0,
        onError: () => {
          redirect()
        },
        onSuccess: (data) => {
          const { detail } = data
          if (detail === 'fail') {
            redirect()
          }
        }
      },
      {
        queryKey: ['methods'],
        queryFn: getMethods,
        keepPreviousData: false,
        cacheTime: 0,
        refetchInterval: 0
      }
    ]
  })

  if (results[0].isLoading || results[1].isLoading) {
    return <LinearProgress />
  }

  const allowedDrawerMethods = filterSidebarList(results[1].data)

  return (
    <Layout>
      <AppBar
        title={title}
        sx={{
          marginLeft: `${drawerWidth}px`,
          width: `calc(100% - ${drawerWidth}px)`
        }}
      />

      <Container maxWidth="xl">
        <Box className="columns" {...props}>
          <Drawer variant="permanent" open list={allowedDrawerMethods} />
          <Box className="main-content">
            <Toolbar />
            {children}
          </Box>
        </Box>
      </Container>
    </Layout>
  )
}

export default AccountLayout
