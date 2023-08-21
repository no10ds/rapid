import {
  AccountLayout,
  Button,
  Card,
  Link,
  Row,
  Select,
  SimpleTable,
  TextField,
  Alert
} from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { asVerticalTableList } from '@/lib'
import { getDatasetInfo, queryDataset } from '@/service'
import { DataFormats } from '@/service/types'
import { Typography, LinearProgress } from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState } from 'react'

function DownloadDataset() {
  const router = useRouter()
  const { layer, domain, dataset } = router.query
  const version = router.query.version ? router.query.version : 0
  const [dataFormat, setDataFormat] = useState<DataFormats>('csv')
  const [queryBody, setQueryBody] = useState({
    select_columns: '',
    filter: '',
    group_by_columns: '',
    aggregation_conditions: '',
    limit: ''
  })

  const {
    isLoading: isDatasetInfoLoading,
    data: datasetInfoData,
    error: datasetInfoError
  } = useQuery(['datasetInfo', layer, domain, dataset, version ? version : 0], getDatasetInfo)

  const { isLoading, mutate, error } = useMutation<
    Response,
    Error,
    { path: string; dataFormat: DataFormats; data: unknown }
  >({
    mutationFn: queryDataset,
    onSuccess: async (response, { dataFormat }) => {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = `${layer}_${domain}_${dataset}_${version}.${dataFormat}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
    }
  })

  if (isDatasetInfoLoading) {
    return <LinearProgress />
  }

  if (datasetInfoError) {
    return <ErrorCard error={datasetInfoError as Error} />
  }

  const addListValueToQuery = (queryBody, key, value) => {
    if (value) {
      queryBody[key] = value.split(',')
    }
  }

  const addStringValueToQuery = (queryBody, key, value) => {
    if (value) {
      queryBody[key] = value
    }
  }

  const createQueryBodyData = () => {
    const queryBodyData = {}
    addListValueToQuery(queryBodyData, 'select_columns', queryBody.select_columns)
    addStringValueToQuery(queryBodyData, 'filter', queryBody.filter)
    addListValueToQuery(queryBodyData, 'group_by_columns', queryBody.group_by_columns)
    addStringValueToQuery(
      queryBodyData,
      'aggregation_conditions',
      queryBody.aggregation_conditions
    )
    addStringValueToQuery(queryBodyData, 'limit', queryBody.limit)
    return queryBodyData
  }

  return (
    <Card
      action={
        <Button
          color="primary"
          onClick={() =>
            mutate({
              path: `${layer}/${domain}/${dataset}/query?version=${version}`,
              dataFormat,
              data: createQueryBodyData()
            })
          }
          loading={isLoading}
        >
          Download
        </Button>
      }
    >
      <Typography variant="h2" gutterBottom>
        Dataset Overview
      </Typography>

      <SimpleTable
        list={asVerticalTableList([
          { name: 'Domain', value: domain as string },
          { name: 'Dataset', value: dataset as string },
          { name: 'Description', value: datasetInfoData.metadata.description },
          { name: 'Version', value: version as string },
          { name: 'Last updated	', value: datasetInfoData.metadata.last_updated },
          {
            name: 'Number of Rows',
            value: datasetInfoData.metadata.number_of_rows.toString()
          },
          {
            name: 'Number of Columns',
            value: datasetInfoData.metadata.number_of_columns.toString()
          }
        ])}
      />

      <Typography variant="h2" gutterBottom>
        Columns
      </Typography>
      <SimpleTable
        sx={{ mb: 4 }}
        headers={[
          { children: 'Name' },
          { children: 'Data Type' },
          { children: 'Allows Null' },
          { children: 'Max' },
          { children: 'Min' }
        ]}
        list={datasetInfoData.columns.map((column) => {
          return [
            { children: column.name },
            { children: column.data_type },
            { children: column.allow_null ? 'True' : 'False' },
            { children: '-' },
            { children: '-' }
          ]
        })}
      />
      <Typography variant="h2" gutterBottom>
        Format
      </Typography>
      <Row>
        <Select
          label="Data format"
          data={['csv', 'json']}
          value={dataFormat}
          onChange={(e) => setDataFormat(e.target.value as DataFormats)}
        />
      </Row>

      <Typography variant="h2" gutterBottom>
        Query (optional)
      </Typography>

      <Typography variant="body2" gutterBottom>
        For further information on writing queries consult the{' '}
        <Link
          href="https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md#how-to-construct-a-query-object"
          target="_blank"
        >
          query writing guide
        </Link>
      </Typography>

      <Row>
        <Typography variant="caption">Select Columns</Typography>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="column1, avg(column2)"
          onChange={(event) =>
            setQueryBody({ ...queryBody, select_columns: event.target.value })
          }
        />
      </Row>

      <Row>
        <Typography variant="caption">Filter</Typography>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="column >= 10"
          onChange={(event) => setQueryBody({ ...queryBody, filter: event.target.value })}
        />
      </Row>

      <Row>
        <Typography variant="caption">Group by Columns</Typography>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="column1, column3"
          onChange={(event) =>
            setQueryBody({ ...queryBody, group_by_columns: event.target.value })
          }
        />
      </Row>

      <Row>
        <Typography variant="caption">Aggregation Conditions</Typography>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="avg(column2) <= 15"
          onChange={(event) =>
            setQueryBody({ ...queryBody, aggregation_conditions: event.target.value })
          }
        />
      </Row>

      <Row>
        <Typography variant="caption">Row Limit</Typography>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="30"
          onChange={(event) => setQueryBody({ ...queryBody, limit: event.target.value })}
        />
      </Row>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error?.message}
        </Alert>
      )}
    </Card>
  )
}

export default DownloadDataset

DownloadDataset.getLayout = (page) => (
  <AccountLayout title="Download">{page}</AccountLayout>
)
