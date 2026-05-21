import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import { deleteDataset, getDatasetsUi } from '@/service'
import { Dataset, DeleteDatasetResponse } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'
import { Box, Alert, AlertTitle, Button, Chip, LinearProgress } from '@mui/material'

function DeleteDataset({ datasetInput = null }: { datasetInput?: Dataset | null }) {
  const router = useRouter()
  const { layer, domain, dataset: datasetName } = router.query ?? {}

  const fromQuery: Dataset | null =
    layer && domain && datasetName
      ? {
          layer: layer as string,
          domain: domain as string,
          dataset: datasetName as string,
          version: 1,
          sensitivity: undefined
        }
      : null

  const [dataset, setDataset] = useState<Dataset | null>(datasetInput ?? fromQuery)
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
    onMutate: () => setDeleteDatasetSuccessDetails(undefined),
    onSuccess: (data) => setDeleteDatasetSuccessDetails(data.details)
  })

  if (isDatasetsListLoading) {
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  return (
    <Box
      component="form"
      sx={{ maxWidth: 860, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}
      onSubmit={async (event) => {
        event.preventDefault()
        if (dataset) {
          await mutate({ path: `${dataset.layer}/${dataset.domain}/${dataset.dataset}` })
        }
      }}
    >
      <Alert severity="error" variant="outlined">
        <AlertTitle sx={{ fontWeight: 600 }}>Destructive action</AlertTitle>
        This action permanently deletes the dataset, its schema, crawlers, and all raw
        data. This <strong>cannot be undone</strong>.
      </Alert>

      <FormCard
        title="Select dataset to delete"
        actionsError={error}
        actions={
          <>
            <Button
              variant="contained"
              color="error"
              type="submit"
              data-testid="submit"
              disabled={!dataset || isLoading}
            >
              {isLoading ? 'Deleting…' : 'Delete dataset'}
            </Button>
            <Button variant="outlined" type="button" onClick={() => router.push('/catalog')}>
              Cancel
            </Button>
            {dataset && !deleteDatasetSuccessDetails && (
              <Chip
                size="small"
                variant="outlined"
                label={`${dataset.layer} / ${dataset.domain} / ${dataset.dataset}`}
                sx={{ ml: 'auto' }}
              />
            )}
          </>
        }
      >
        {fromQuery ? (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip size="small" variant="outlined" label={`Layer: ${fromQuery.layer}`} />
            <Chip size="small" variant="outlined" label={`Domain: ${fromQuery.domain}`} />
            <Chip size="small" variant="outlined" label={`Dataset: ${fromQuery.dataset}`} />
          </Box>
        ) : (
          <DatasetSelector
            datasetsList={datasetsList}
            setParentDataset={setDataset}
            enableVersionSelector={false}
          />
        )}

        {deleteDatasetSuccessDetails && (
          <Alert severity="success" variant="outlined" sx={{ mt: 2 }} data-testid="delete-status">
            Dataset deleted: {dataset
              ? `${dataset.layer}/${dataset.domain}/${dataset.dataset}`
              : deleteDatasetSuccessDetails}
          </Alert>
        )}
      </FormCard>
    </Box>
  )
}

export default DeleteDataset

DeleteDataset.getLayout = (page: ReactNode) => (
  <AccountLayout title="Delete Data">{page}</AccountLayout>
)
