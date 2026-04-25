import { Card } from '@/components'
import AccountLayout from '@/components/Layout/AccountLayout'
import { useRouter } from 'next/router'

function SuccessPage() {
  const router = useRouter()

  return (
    <Card>
      <h1>Success - Created</h1>
      <p>You will only see this page once. Please make note of the details below.</p>

      {Object.keys(router.query).map((key, index) => (
        <p key={index}>
          <b>{key}:</b> {router.query[key]}
        </p>
      ))}
    </Card>
  )
}

export default SuccessPage

SuccessPage.getLayout = (page) => (
  <AccountLayout title="Create User">{page}</AccountLayout>
)
