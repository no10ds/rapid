import {
  Card,
  SimpleTable,
  AccountLayout,
  Button,
  Select,
  Link,
  Row,
  TextField
} from '@/components'
import { Typography } from '@mui/material'
import { useRouter } from 'next/router'
import { asVerticalTableList } from '@/lib'

function FilePage() {
  const router = useRouter()
  const { dataset, version } = router.query

  return (
    <Card action={<Button color="primary">Download</Button>}>
      <Typography variant="h2" gutterBottom>
        Dataset Overview
      </Typography>

      <SimpleTable
        list={asVerticalTableList([
          { name: 'Domain', value: 'automotive' },
          { name: 'Dataset', value: dataset?.toString() },
          { name: 'Version', value: version?.toString() },
          { name: 'Last updated	', value: '15 Sep 2022 at 11:18:37' },
          { name: 'Number of Rows', value: '990300' },
          { name: 'Number of Columns', value: '17' }
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
          { children: 'Allows Max' },
          { children: 'Allows Min' }
        ]}
        list={[
          [
            { children: 'brand' },
            { children: 'object' },
            { children: 'True' },
            { children: '-' },
            { children: '-' }
          ],
          [
            { children: 'name' },
            { children: 'object' },
            { children: 'True' },
            { children: '-' },
            { children: '-' }
          ],
          [
            { children: 'bodytype' },
            { children: 'object' },
            { children: 'True' },
            { children: '-' },
            { children: '-' }
          ]
        ]}
      />
      <Typography variant="h2" gutterBottom>
        Format
      </Typography>
      <Row>
        <Select label="Data format" data={['csv', 'json']} />
      </Row>

      <Typography variant="h2" gutterBottom>
        Query (optional)
      </Typography>

      <Typography variant="body2" gutterBottom>
        For further information on writing queries consult the{' '}
        <Link
          href="https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md#query-structure"
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
        />
      </Row>

      <Row>
        <Typography variant="caption">Filter</Typography>
        <TextField fullWidth size="small" variant="outlined" placeholder="column >= 10" />
      </Row>

      <Row>
        <Typography variant="caption">Group by Columns</Typography>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="column1, column3"
        />
      </Row>

      <Row>
        <Typography variant="caption">Aggregation Conditions</Typography>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="avg(column2) <= 15"
        />
      </Row>

      <Row>
        <Typography variant="caption">Row Limit</Typography>
        <TextField fullWidth size="small" variant="outlined" placeholder="30" />
      </Row>
    </Card>
  )
}

export default FilePage

FilePage.getLayout = (page) => <AccountLayout title="Download">{page}</AccountLayout>
