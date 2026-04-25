import { Button, PublicLayout } from '@/components'
import { useState } from 'react'
import { useQueries } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { getAuthStatus, getLogin } from '@/service'

const IndexPage = () => {
  const [authUrl, setAuthUrl] = useState('/login')
  const router = useRouter()

  const results = useQueries({
    queries: [
      {
        queryKey: ['authStatus'],
        queryFn: getAuthStatus,
        keepPreviousData: false,
        cacheTime: 0,
        refetchInterval: 0,
        onSuccess: (data) => {
          const { detail } = data
          if (detail === 'success') {
            router.replace({
              pathname: '/'
            })
          }
        }
      },
      {
        queryKey: ['loginLink'],
        queryFn: getLogin,
        onSuccess: (data) => {
          setAuthUrl(data.auth_url)
        },
        keepPreviousData: false,
        cacheTime: 0,
        refetchInterval: 0
      }
    ]
  })

  if (results[0].isLoading || results[1].isLoading) {
    return <p role="progressbar">Loading...</p>
  }

  return (
    <>
      <Button
        href={authUrl}
        color="primary"
        size="large"
        fullWidth
        disableRoute
        data-testid="login-link"
      >
        Login
      </Button>
    </>
  )
}

export default IndexPage
IndexPage.getLayout = (page) => (
  <PublicLayout
    title="Welcome Back"
    promo={
      <>
        <p>
          Project rAPId aims to create consistent, secure, interoperable data storage and
          sharing interfaces (APIs) that enable departments to discover, manage and share
          data and metadata amongst themselves.
        </p>

        <p>
          This will improve the government's use of data by making it more scalable,
          secure, and resilient, helping to match the rising demand for good-quality
          evidence in the design, delivery, and evaluation of public policy.
        </p>

        <p>
          The project aims to deliver a replicable template for simple data storage
          infrastructure in AWS, a RESTful API and custom frontend UI to ingest and share
          named, standardised datasets.
        </p>
      </>
    }
  >
    {page}
  </PublicLayout>
)
