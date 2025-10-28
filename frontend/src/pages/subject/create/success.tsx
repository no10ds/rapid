import { Card } from '@/components'
import AccountLayout from '@/components/Layout/AccountLayout'
import { Typography } from '@mui/material'
import { useRouter } from 'next/router'

function SuccessPage() {
  const router = useRouter()

  return (
    <Card>
      <Typography variant="h1" gutterBottom>
        Success - Created
      </Typography>
      <Typography gutterBottom>
        You will only see this page once. Please make note of the details below.
      </Typography>

      {Object.keys(router.query).map((key, index) => {
        return (
          <Typography variant="body2" key={index}>
            <b>{key}:</b> {router.query[key]}
          </Typography>
        )
      })}
    </Card>
  )
}

export default SuccessPage

SuccessPage.getLayout = (page) => (
  <AccountLayout title="Create User">{page}</AccountLayout>
)
