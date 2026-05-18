import { useState } from 'react'
import { useQueries } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { getAuthStatus, getLogin } from '@/service'
import Image from 'next/image'

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
      <div className="login-page">
        <div className="login-glow" />
        <div className="rapid-loading-bar" role="progressbar" />
      </div>
    )
  }

  return (
    <div className="login-page">
      <div className="login-glow" />
      <div className="login-card">
        <div className="login-logo">
          <Image
            src="/img/logo.png"
            alt="rAPId"
            width={140}
            height={36}
            style={{ objectFit: 'contain' }}
            priority
          />
        </div>
        <h1 className="login-title">Welcome back</h1>
        <p className="login-sub">Sign in to access your datasets and manage your data.</p>
        <a href={authUrl} className="login-btn" data-testid="login-link">
          Sign in
        </a>
      </div>
    </div>
  )
}

export default LoginPage
