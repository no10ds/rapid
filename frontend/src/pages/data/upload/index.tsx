import { AccountLayout, FormCard } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import UploadProgress from '@/components/UploadProgress/UploadProgress'
import { getDatasetsUi, uploadDataset } from '@/service'
import {
  Dataset,
  UploadDatasetResponse,
  UploadDatasetResponseDetails
} from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useState, ReactNode } from 'react'
import Link from 'next/link'
import { Box, Typography, Button, Chip, Alert, LinearProgress } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import AddIcon from '@mui/icons-material/Add'

function UploadDataset({ datasetInput = null }: { datasetInput?: Dataset | null }) {
  const [file, setFile] = useState<File | undefined>()
  const [dataset, setDataset] = useState<Dataset | null>(datasetInput)
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
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  const datasetLabel = dataset
    ? `${dataset.layer} / ${dataset.domain} / ${dataset.dataset}`
    : null

  return (
    <Box
      component="form"
      sx={{ maxWidth: 860, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}
      onSubmit={async (event) => {
        event.preventDefault()
        if (dataset && file) {
          const formData = new FormData()
          formData.append('file', file)
          await mutate({
            path: `${dataset.layer}/${dataset.domain}/${dataset.dataset}?version=${dataset.version}`,
            data: formData
          })
        }
      }}
    >
      <FormCard num={1} title="Select dataset">
        <DatasetSelector datasetsList={datasetsList} setParentDataset={setDataset} />
        <Box
          sx={{
            mt: 2,
            p: 1.5,
            border: '1px dashed',
            borderColor: 'divider',
            borderRadius: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 1.5,
            bgcolor: 'background.default'
          }}
        >
          <Typography variant="body2" sx={{ fontSize: 12 }}>
            Can&apos;t find your dataset? You&apos;ll need to add it first.
          </Typography>
          <Button
            component={Link}
            href="/schema/create"
            size="small"
            variant="outlined"
            startIcon={<AddIcon />}
          >
            Add new dataset
          </Button>
        </Box>
      </FormCard>

      <FormCard
        num={2}
        title="Upload file"
        actionsError={error}
        actions={
          <>
            <Button
              variant="contained"
              type="submit"
              disabled={!dataset || !file || isLoading || disable}
              data-testid="submit"
            >
              {isLoading ? 'Uploading…' : 'Upload dataset'}
            </Button>
            <Button
              variant="outlined"
              type="button"
              onClick={() => {
                setFile(undefined)
                setDataset(null)
                setDisable(false)
                setUploadSuccessDetails(undefined)
              }}
            >
              Cancel
            </Button>
            {dataset && (
              <Chip size="small" variant="outlined" label={datasetLabel} sx={{ ml: 'auto' }} />
            )}
          </>
        }
      >
        {datasetLabel && (
          <Alert severity="info" variant="outlined" sx={{ mb: 2 }}>
            <strong>Selected dataset:</strong> {datasetLabel}
          </Alert>
        )}

        {!disable && (
          <Box
            component="label"
            htmlFor="file"
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1,
              p: 4,
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              bgcolor: 'background.default',
              '&:hover': { borderColor: 'primary.main' }
            }}
          >
            <CloudUploadIcon sx={{ fontSize: 32, color: 'text.disabled' }} />
            <Typography variant="body1" sx={{ fontSize: 13, fontWeight: 500 }}>
              Drag &amp; drop your CSV file here
            </Typography>
            <Typography variant="body2" sx={{ fontSize: 11, color: 'text.disabled' }}>
              or click to browse — CSV only, max 100 MB
            </Typography>
            {file && (
              <Typography
                variant="body2"
                sx={{ fontSize: 12, color: 'primary.main', fontWeight: 500 }}
              >
                {file.name}
              </Typography>
            )}
          </Box>
        )}
        <input
          name="file"
          id="file"
          type="file"
          data-testid="upload"
          style={{ display: 'none' }}
          onChange={(event) => setFile(event.target.files[0])}
          key={`file-upload-${disable.toString()}`}
        />

        {uploadSuccessDetails && (
          <Box sx={{ mt: 2 }}>
            <UploadProgress
              uploadSuccessDetails={uploadSuccessDetails}
              setDisableUpload={setDisable}
            />
          </Box>
        )}
      </FormCard>
    </Box>
  )
}

export default UploadDataset

UploadDataset.getLayout = (page: ReactNode) => (
  <AccountLayout title="Upload Data">{page}</AccountLayout>
)
