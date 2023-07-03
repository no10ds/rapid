import { Card, Row, Button, Select } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import AccountLayout from '@/components/Layout/AccountLayout'
import { getDatasetsUi } from '@/service'
import { FormControl, Typography, LinearProgress } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

function DownloadData() {
  const router = useRouter()
  const [dataset, setDataset] = useState<string>('')
  const [versions, setVersions] = useState(0)
  const [versionSelected, setVersionSelected] = useState(0)

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  useEffect(() => {
    if (datasetsList && Object.keys(datasetsList).length > 0) {
      const firstKey = Object.keys(datasetsList)[0]
      setDataset(`${firstKey}/${datasetsList[firstKey][0].dataset}`)
    }
  }, [datasetsList])

  useEffect(() => {
    let version = 0
    if (dataset) {
      const splits = dataset.split('/')
      const domain = splits[0]
      const _dataset = splits[1]
      version = parseInt(
        datasetsList[domain].filter((item) => item.dataset === _dataset)[0].version
      )
    }
    setVersions(version)
    setVersionSelected(version ? Array(version).length : 0)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataset])

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
      action={
        <Button
          data-testid="submit"
          color="primary"
          onClick={() =>
            router.push(`/data/download/${dataset}?version=${versionSelected}`)
          }
        >
          Next
        </Button>
      }
    >
      <Typography variant="body1" gutterBottom>
        Download the contents of a datasource from rAPId. Select the relevant dataset you
        want to download and then the version to download from. Please note it might take
        some time to for the API to query the dataset especially if they are large.
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

      {versions && (
        <>
          <Typography variant="h2">Select version</Typography>

          <Row>
            <Select
              label="Select version"
              onChange={(event) => setVersionSelected(event.target.value as number)}
              native
              inputProps={{ 'data-testid': 'select-version' }}
            >
              {Array(versions)
                .fill(0)
                .map((_, index, array) => (
                  <option value={array.length - index} key={index}>
                    {array.length - index}
                  </option>
                ))}
            </Select>
          </Row>
        </>
      )}
    </Card>
  )
}

export default DownloadData

DownloadData.getLayout = (page) => (
  <AccountLayout title="Download Data">{page}</AccountLayout>
)
