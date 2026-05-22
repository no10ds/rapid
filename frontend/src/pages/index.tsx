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
    <Box data-testid="intro" sx={{ width: '100%' }}>
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1e3a5f 0%, #2a4a72 100%)',
          color: '#fff',
          px: 4,
          py: 8,
          textAlign: 'center'
        }}
      >
        <Typography variant="h1" sx={{ color: '#fff', fontSize: 32, mb: 4 }}>
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
