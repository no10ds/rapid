import AccountLayout from '@/components/Layout/AccountLayout'
import DatasetSearchBar from '@/components/DatasetSearchBar/DatasetSearchBar'
import { useQuery } from '@tanstack/react-query'
import { getMethods, getDatasetsUi } from '@/service'
import { Dataset } from '@/service/types'
import { ReactNode } from 'react'
import { Box, Typography, LinearProgress } from '@mui/material'

function AccountIndexPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['methods'],
    queryFn: getMethods
  })

  const canRead = data?.can_download || data?.can_search_catalog
  const canWrite = data?.can_upload

  const { data: readDatasets } = useQuery(
    ['datasetsList', 'READ'],
    getDatasetsUi,
    { enabled: !!canRead }
  )

  const { data: writeDatasets } = useQuery(
    ['datasetsList', 'WRITE'],
    getDatasetsUi,
    { enabled: !!canWrite && !canRead }
  )

  const datasets: Dataset[] = (readDatasets ?? writeDatasets ?? []) as Dataset[]

  if (isLoading) {
    return <LinearProgress color="primary" role="progressbar" />
  }

  return (
    <Box
      data-testid="intro"
      sx={{
        width: '100%',
        minHeight: '100%',
        bgcolor: 'secondary.main',
        color: '#fff',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
        px: 3,
        pt: '80px',
        pb: '120px'
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 720, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
        <Typography
          variant="h1"
          sx={{
            color: '#f1f3f5',
            fontSize: 36,
            fontWeight: 700,
            letterSpacing: '-0.03em',
            lineHeight: 1.15,
            mb: '14px'
          }}
        >
          Welcome to rAPId
        </Typography>
        <DatasetSearchBar datasets={datasets} />
      </Box>

      {(data?.can_upload || data?.can_download) && <span data-testid="data-management" />}
      {data?.can_create_schema && <span data-testid="schema-management" />}
      {data?.can_manage_users && <span data-testid="user-management" />}
    </Box>
  )
}

export default AccountIndexPage

AccountIndexPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Dashboard" noPad>{page}</AccountLayout>
)
