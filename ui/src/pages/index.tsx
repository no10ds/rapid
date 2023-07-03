import { Typography, Grid, Stack, LinearProgress } from '@mui/material'
import Image, { StaticImageData } from 'next/image'
import AccountLayout from '@/components/Layout/AccountLayout'
import { Link, Row } from '@/components'
import userIcon from '../../public/img/user_icon.png'
import dataIcon from '../../public/img/data_icon.png'
import schemaIcon from '../../public/img/schema_icon.png'
import taskIcon from '../../public/img/task_icon.png'
import { ComponentProps, ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getMethods } from '@/service'

function ManagementCard({
  iconImage,
  title,
  children,
  ...rest
}: {
  iconImage: StaticImageData
  title: string
  children: ReactNode
} & ComponentProps<typeof Grid>) {
  return (
    <Grid item xs={6} {...rest}>
      <Stack direction="row" spacing={2}>
        <Image src={iconImage} width={120} height={120} alt="User Management" />
        <Stack>
          <Typography variant="h2">{title}</Typography>
          {children}
        </Stack>
      </Stack>
    </Grid>
  )
}

function AccountIndexPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['methods'],
    queryFn: getMethods,
    keepPreviousData: false,
    cacheTime: 0,
    refetchInterval: 0
  })

  if (isLoading) {
    return <LinearProgress />
  }

  return (
    <div>
      <Typography variant="h1" gutterBottom>
        Welcome to rAPId
      </Typography>

      <div style={{ marginBottom: '3rem ' }} data-testid="intro">
        <Typography variant="h2">Getting Started</Typography>
        <Typography paragraph>
          With rAPId, users and clients can ingest, validate and query data via an API.
          The rAPId web application makes interactions with the API quicker and easier.
        </Typography>
        <Typography paragraph gutterBottom>
          To read more about the API or for technical architecture, see the links below.
          Otherwise, to get started choose an action from the menu below.
        </Typography>

        <Stack sx={{ marginBottom: '1rem' }} spacing={1}>
          <Link color="inherit" href={`/api/docs`} variant="body1">
            View the API docs
          </Link>
          <Link
            color="inherit"
            href="https://github.com/no10ds/rapid-api"
            variant="body1"
          >
            See the source code
          </Link>
          <Link
            color="inherit"
            href="https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md"
            variant="body1"
          >
            View the rAPId Architecture
          </Link>
          <Link
            color="inherit"
            href="https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM"
            variant="body1"
          >
            Contact
          </Link>
        </Stack>
      </div>

      <Row>
        <Grid container spacing={4}>
          {data.can_manage_users && (
            <ManagementCard
              iconImage={userIcon}
              title="User Management"
              data-testid="user-management"
            >
              <>
                <Typography paragraph>
                  Create and modify different users and clients.
                </Typography>
                <Link color="inherit" href="/subject/create">
                  Create User
                </Link>
                <Link color="inherit" href="/subject/modify">
                  Modify User
                </Link>
              </>
            </ManagementCard>
          )}

          {(data.can_upload || data.can_download) && (
            <>
              <ManagementCard
                iconImage={dataIcon}
                title="Data Management"
                data-testid="data-management"
              >
                <>
                  <Typography paragraph>
                    Upload and download existing data files.
                  </Typography>
                  {data.can_download && (
                    <Link color="inherit" href="/data/download">
                      Download Data
                    </Link>
                  )}

                  {data.can_download && (
                    <Link color="inherit" href="/data/upload">
                      Upload Data
                    </Link>
                  )}
                </>
              </ManagementCard>

              {data.can_create_schema && (
                <ManagementCard
                  iconImage={schemaIcon}
                  title="Schema Management"
                  data-testid="schema-management"
                >
                  <>
                    <Typography paragraph>
                      Manually create new schemas from raw data.
                    </Typography>
                    <Link color="inherit" href="/schema/create">
                      Create Schema
                    </Link>
                  </>
                </ManagementCard>
              )}

              <ManagementCard
                iconImage={taskIcon}
                title="Task Status"
                data-testid="task-status"
              >
                <>
                  <Typography paragraph>View pending and complete api tasks.</Typography>
                  <Link color="inherit" href="/tasks">
                    Tasks
                  </Link>
                </>
              </ManagementCard>
            </>
          )}
        </Grid>
      </Row>
    </div>
  )
}

export default AccountIndexPage

AccountIndexPage.getLayout = (page) => (
  <AccountLayout title="Dashboard">{page}</AccountLayout>
)
