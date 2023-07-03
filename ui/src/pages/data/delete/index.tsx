import { AccountLayout, Alert, Button, Card, Row, Select } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { deleteDataset, getDatasetsUi } from '@/service'
import { DeleteDatasetResponse } from '@/service/types'
import { FormControl, LinearProgress, Typography } from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'

function DeleteDataset() {
  const [dataset, setDataset] = useState<string>('')
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

  useEffect(() => {
    if (datasetsList && Object.keys(datasetsList).length > 0) {
      const firstKey = Object.keys(datasetsList)[0]
      setDataset(`${firstKey}/${datasetsList[firstKey][0].dataset}`)
    }
  }, [datasetsList])

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
        await mutate({ path: dataset })
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

        <Row>
          <FormControl fullWidth size="small">
            <Select
              label="Select a dataset"
              onChange={(event) => setDataset(event.target.value as string)}
              native
              inputProps={{ 'data-testid': 'select-dataset' }}
            >
              {Object.keys(datasetsList).map((key) => (
                <optgroup label={key} key={key}>
                  {datasetsList[key].map((item) => (
                    <option value={`${key}/${item.dataset}`} key={item.dataset}>
                      {item.dataset}
                    </option>
                  ))}
                </optgroup>
              ))}
            </Select>
          </FormControl>
        </Row>

        {deleteDatasetSuccessDetails ? (
          <Alert
            title={`Dataset deleted: ${dataset}`}
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
