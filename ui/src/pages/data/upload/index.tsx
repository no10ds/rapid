import { Card, Row, Button, Select, Alert, Link } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import AccountLayout from '@/components/Layout/AccountLayout'
import UploadProgress from '@/components/UploadProgress/UploadProgress'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import { getDatasetsUi, uploadDataset } from '@/service'
import { Dataset, UploadDatasetResponse, UploadDatasetResponseDetails } from '@/service/types'
import { Typography, LinearProgress } from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'


function UploadDataset({ datasetInput = null }: { datasetInput?: Dataset }) {
  const [file, setFile] = useState<File | undefined>()
  const [dataset, setDataset] = useState<Dataset>(datasetInput)
  const [disable, setDisable] = useState<boolean>(false)
  const [uploadSuccessDetails, setUploadSuccessDetails] = useState<
    UploadDatasetResponseDetails | undefined
  >()

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'WRITE'], getDatasetsUi)

  const { isLoading, mutate, error } = useMutation<
    UploadDatasetResponse,
    Error,
    { path: string; data: FormData }
  >({
    mutationFn: uploadDataset,
    onMutate: () => {
      setUploadSuccessDetails(undefined)
    },
    onSuccess: (data) => {
      setUploadSuccessDetails(data.details)
      setDisable(true)
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
        const formData = new FormData()
        formData.append('file', file)
        await mutate({ path: `${dataset.layer}/${dataset.domain}/${dataset.dataset}?version=${dataset.version}`, data: formData })
      }}
    >
      <Card
        action={!disable &&
          <Button color="primary" type="submit" loading={isLoading} data-testid="submit">
            Upload dataset
          </Button>
        }
      >
        <Typography variant="body1" gutterBottom>
          Upload a new file to the selected data source. It assumes a given a schema has
          been uploaded for the data source and the data to upload matches this schema.
        </Typography>

        <DatasetSelector datasetsList={datasetsList} setParentDataset={setDataset}></DatasetSelector>

        <Row>
          {!disable &&
            <input
              name="file"
              id="file"
              type="file"
              data-testid="upload"
              onChange={(event) => setFile(event.target.files[0])}
              // This key changing resets the file so that after an upload event it is removed
              key={`file-upload-${disable.toString()}`}
            />}
        </Row>

        {uploadSuccessDetails ? (
          <UploadProgress uploadSuccessDetails={uploadSuccessDetails} setDisableUpload={setDisable} />
        ) : null}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error?.message}
          </Alert>
        )}
      </Card>
    </form >
  )
}

export default UploadDataset

UploadDataset.getLayout = (page) => <AccountLayout title="Upload">{page}</AccountLayout>
