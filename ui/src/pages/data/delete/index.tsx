import { AccountLayout, Alert, Button, Card } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import { deleteDataset, getDatasetsUi } from '@/service'
import { Dataset, DeleteDatasetResponse } from '@/service/types'
import { LinearProgress, Typography } from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'

function DeleteDataset({ datasetInput = null }: { datasetInput?: Dataset }) {
  const [dataset, setDataset] = useState<Dataset>(datasetInput)
  const [deleteDatasetSuccessDetails, setDeleteDatasetSuccessDetails] = useState<
    string | undefined
  >()

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  const { isLoading, mutate, error } = useMutation<
    DeleteDatasetResponse,
    Error,
    { path: string }
  >({
    mutationFn: deleteDataset,
    onMutate: () => {
      setDeleteDatasetSuccessDetails(undefined)
    },
    onSuccess: (data) => {
      setDeleteDatasetSuccessDetails(data.details)
    }
  })

  if (isDatasetsListLoading) {
    return <LinearProgress />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  return (
    <form
      onSubmit={async (event) => {
        event.preventDefault()
        await mutate({ path: `${dataset.layer}/${dataset.domain}/${dataset.dataset}` })
      }}
    >
      <Card
        action={
          <Button data-testid="submit" color="primary" type="submit" loading={isLoading}>
            Delete
          </Button>
        }
      >
        <Typography variant="body1" gutterBottom>
          Delete all the contents of a datasource from rAPId. Select the relevant dataset
          you want to delete. Please note this also deletes the schemas relating to this
          dataset and the underlying crawlers and raw data.
        </Typography>

        <DatasetSelector datasetsList={datasetsList} setParentDataset={setDataset} enableVersionSelector={false}></DatasetSelector>

        {deleteDatasetSuccessDetails ? (
          <Alert
            title={`Dataset deleted: ${dataset.layer}/${dataset.domain}/${dataset.dataset}`}
            data-testid="delete-status"
          ></Alert>
        ) : null}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error.message}
          </Alert>
        )}
      </Card>
    </form>
  )
}

export default DeleteDataset

DeleteDataset.getLayout = (page) => (
  <AccountLayout title="Delete Data">{page}</AccountLayout>
)
