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
import { useRouter } from 'next/router'
import { asVerticalTableList } from '@/utils'

function FilePage() {
  const router = useRouter()
  const { dataset, version } = router.query

  return (
    <Card action={<Button color="primary">Download</Button>}>
      <h2>Dataset Overview</h2>

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

      <h2>Columns</h2>
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
      <h2>Format</h2>
      <Row>
        <Select label="Data format" data={['csv', 'json']} />
      </Row>

      <h2>Query (optional)</h2>

      <p>
        For further information on writing queries consult the{' '}
        <Link href="https://rapid.readthedocs.io/en/latest/api/query/" target="_blank">
          query writing guide
        </Link>
      </p>

      <Row>
        <label>Select Columns</label>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="column1, avg(column2)"
        />
      </Row>

      <Row>
        <label>Filter</label>
        <TextField fullWidth size="small" variant="outlined" placeholder="column >= 10" />
      </Row>

      <Row>
        <label>Group by Columns</label>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="column1, column3"
        />
      </Row>

      <Row>
        <label>Aggregation Conditions</label>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="avg(column2) <= 15"
        />
      </Row>

      <Row>
        <label>Row Limit</label>
        <TextField fullWidth size="small" variant="outlined" placeholder="30" />
      </Row>
    </Card>
  )
}

export default FilePage

FilePage.getLayout = (page) => <AccountLayout title="Download">{page}</AccountLayout>
