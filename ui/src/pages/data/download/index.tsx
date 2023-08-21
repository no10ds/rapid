import { Card, Button } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import AccountLayout from '@/components/Layout/AccountLayout'
import { getDatasetsUi } from '@/service'
import { Typography, LinearProgress } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState } from 'react'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import { Dataset } from '@/service/types'



function DownloadData({ datasetInput = null }: { datasetInput?: Dataset }) {
  const router = useRouter()
  const [dataset, setDataset] = useState<Dataset>(datasetInput)

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  if (isDatasetsListLoading) {
    return <LinearProgress />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  if (Object.keys(datasetsList).length === 0) {
    return (
      <Card data-testid="no-data-helper">
        <Typography variant="body1" gutterBottom>
          You currently do not have any data to download. Get started by creating a schema
          and uploading a dataset that you want to store in rAPId.
        </Typography>
        <Typography variant="body1" gutterBottom>
          All datasets will then become available to be downloaded from here.
        </Typography>
      </Card>
    )
  }

  return (
    <Card
      action={<Button
        data-testid="submit"
        color="primary"
        onClick={() =>
          router.push(`/data/download/${dataset.layer}/${dataset.domain}/${dataset.dataset}?version=${dataset.version}`)
        }
      >
        Next
      </Button>}
    >
      <Typography variant="body1" gutterBottom>
        Download the contents of a datasource from rAPId. Select the relevant dataset you
        want to download and then the version to download from. Please note it might take
        some time to for the API to query the dataset especially if they are large.
      </Typography>
      <DatasetSelector datasetsList={datasetsList} setParentDataset={setDataset}></DatasetSelector>
    </Card>
  )
}

export default DownloadData

DownloadData.getLayout = (page) => (
  <AccountLayout title="Download Data">{page}</AccountLayout>
)
