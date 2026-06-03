import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import { getDatasetsUi } from '@/service'
import { Dataset } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'
import { Box, Paper, Typography, Button, Chip, LinearProgress } from '@mui/material'

function DownloadData({ datasetInput = null }: { datasetInput?: Dataset | null }) {
  const router = useRouter()
  const [dataset, setDataset] = useState<Dataset | null>(datasetInput)

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  if (isDatasetsListLoading) {
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  if (Object.keys(datasetsList).length === 0) {
    return (
      <Paper variant="outlined" sx={{ maxWidth: 860, mx: 'auto', p: 2 }} data-testid="no-data-helper">
        <Typography variant="body2" sx={{ fontSize: 13, mb: 1 }}>
          You currently do not have any data to download. Get started by creating a schema
          and uploading a dataset that you want to store in rAPId.
        </Typography>
        <Typography variant="body2" sx={{ fontSize: 13 }}>
          All datasets will then become available to be downloaded from here.
        </Typography>
      </Paper>
    )
  }

  const datasetLabel = dataset
    ? `${dataset.layer} / ${dataset.domain} / ${dataset.dataset}`
    : null

  return (
    <Box
      component="form"
      sx={{ maxWidth: 860, mx: 'auto' }}
      onSubmit={(event) => {
        event.preventDefault()
        if (dataset) {
          router.push(
            `/data/download/${dataset.layer}/${dataset.domain}/${dataset.dataset}?version=${dataset.version}`
          )
        }
      }}
    >
      <FormCard
        title="Select dataset"
        actions={
          <>
            <Button variant="contained" type="submit" data-testid="submit" disabled={!dataset}>
              Next
            </Button>
            {datasetLabel && (
              <Chip size="small" variant="outlined" label={datasetLabel} sx={{ ml: 'auto' }} />
            )}
          </>
        }
      >
        <Typography variant="body2" sx={{ fontSize: 13, mb: 2 }}>
          Download the contents of a datasource from rAPId. Select the relevant dataset
          and version to download from. Large datasets may take some time to query.
        </Typography>
        <DatasetSelector datasetsList={datasetsList} setParentDataset={setDataset} />
      </FormCard>
    </Box>
  )
}

export default DownloadData

DownloadData.getLayout = (page: ReactNode) => (
  <AccountLayout title="Download Data">{page}</AccountLayout>
)
