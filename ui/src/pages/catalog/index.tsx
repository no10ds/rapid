import { AccountLayout, Button, Row, Card, TextField } from '@/components'
import { zodResolver } from '@hookform/resolvers/zod'
import { Typography } from '@mui/material'
import { useRouter } from 'next/router'
import { useForm, Controller } from 'react-hook-form'
import { z } from 'zod'

function CatalogPage() {
  const router = useRouter()

  const { control, handleSubmit } = useForm<{ search: string }>({
    resolver: zodResolver(
      z.object({
        search: z.string()
      })
    )
  })

  return (
    <form
      onSubmit={handleSubmit(async (data) => {
        router.push(`/catalog/${data.search}`)
      })}
    >
      <Card
        action={
          <Button color="primary" type="submit">
            Search Catalog
          </Button>
        }
      >
        <Typography variant="h2" gutterBottom>
          Data Catalog Search
        </Typography>

        <Row>
          <Controller
            name="search"
            control={control}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Search Term</Typography>
                <TextField
                  {...field}
                  fullWidth
                  size="small"
                  variant="outlined"
                  placeholder="Catalog Search Term"
                  error={!!error}
                  helperText={error?.message}
                />
              </>
            )}
          />
        </Row>
      </Card>
    </form>
  )
}

export default CatalogPage

CatalogPage.getLayout = (page) => (
  <AccountLayout title="Data Catalog">{page}</AccountLayout>
)
