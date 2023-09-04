import { AccountLayout, Card, SimpleTable } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getMetadataSearch } from '@/service'
import { Chip, LinearProgress, Typography } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'

function GetSearch() {
  const router = useRouter()
  const { search } = router.query

  const { isLoading, data, error } = useQuery(
    ['metadataSearch', search],
    getMetadataSearch,
    {
      refetchOnMount: false
    }
  )

  if (isLoading) {
    return <LinearProgress />
  }

  if (error) {
    return <ErrorCard error={error as Error} />
  }

  if (!data.length) {
    return (
      <Card data-testid="empty-search-content">
        <Typography variant="h2" gutterBottom>
          No Results Found
        </Typography>
        <Typography gutterBottom>Try a less specific query</Typography>
      </Card>
    )
  }

  const getChipLabel = (type) => {
    if (type === 'Columns') {
      return 'Column'
    } else if (type === 'Dataset') {
      return 'Dataset Title'
    } else if (type === 'Description') {
      return 'Description'
    }
  }

  const getChipColor = (type) => {
    if (type === 'Columns') {
      return 'error'
    } else if (type === 'Dataset') {
      return 'primary'
    } else if (type === 'Description') {
      return 'warning'
    }
  }

  return (
    <Card>
      <Typography variant="h2" gutterBottom>
        Data Catalog Search
      </Typography>
      <Typography gutterBottom>Search Term - {search}</Typography>

      <SimpleTable
        sx={{ mb: 4 }}
        list={data.map((item) => {
          return [
            { children: item.domain },
            { children: item.dataset },
            { children: item.version },
            { children: item.matching_data },
            {
              children: (
                <Chip
                  label={getChipLabel(item.matching_field)}
                  color={getChipColor(item.matching_field)}
                  size="small"
                />
              )
            }
          ]
        })}
        headers={[
          { children: 'Dataset Domain' },
          { children: 'Dataset Title' },
          { children: 'Version' },
          { children: 'Match Result' },
          { children: 'Type' }
        ]}
      />
    </Card>
  )
}

export default GetSearch

GetSearch.getLayout = (page) => <AccountLayout title="Data Catalog">{page}</AccountLayout>
