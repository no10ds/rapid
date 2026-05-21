import { useState } from 'react'
import { useQueries } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { getAuthStatus, getLogin } from '@/service'
import Image from 'next/image'
import { Box, Typography, Button, LinearProgress } from '@mui/material'
import { CenteredGradientPage } from '@/components'

const LoginPage = () => {
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
            router.replace({ pathname: '/' })
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
    return (
      <CenteredGradientPage width={320}>
        <LinearProgress color="primary" role="progressbar" />
      </CenteredGradientPage>
    )
  }

  return (
    <CenteredGradientPage>
      <Box sx={{ mb: 3 }}>
        <Image
          src="/img/logo.png"
          alt="rAPId"
          width={140}
          height={36}
          style={{ objectFit: 'contain' }}
          priority
        />
      </Box>
      <Typography variant="h1" sx={{ fontSize: 22, mb: 1 }}>Welcome back</Typography>
      <Typography variant="body2" sx={{ fontSize: 13, mb: 3 }}>
        Sign in to access your datasets and manage your data.
      </Typography>
      <Button
        component="a"
        href={authUrl}
        variant="contained"
        fullWidth
        data-testid="login-link"
      >
        Sign in
      </Button>
    </CenteredGradientPage>
  )
}

export default LoginPage
