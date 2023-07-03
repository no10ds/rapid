import { ThemeProvider } from '@/components'
import { CacheProvider, EmotionCache } from '@emotion/react'
import createEmotionCache from '@/lib/createEmotionCache'
import { ErrorBoundary } from 'react-error-boundary'
import { ReactNode, useEffect } from 'react'
import { AppProps } from 'next/app'
import { NextPage } from 'next'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Head from 'next/head'
import { useRouter } from 'next/router'
import ErrorBoundryComponent from '@/components/ErrorBoundryComponent'

interface MyAppProps extends AppProps {
  emotionCache?: EmotionCache

  Component: NextPage & {
    getLayout?: (page: ReactNode) => ReactNode
  }
}

const clientSideEmotionCache = createEmotionCache()

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 1000, cacheTime: 0, retry: false } }
})

export default function MyApp({
  Component,
  emotionCache = clientSideEmotionCache,
  pageProps
}: MyAppProps) {
  const router = useRouter()
  const { asPath } = router
  const getLayout = Component.getLayout ?? ((page) => page)

  let timeout: NodeJS.Timeout | null = null

  const isLongTimeout = () => {
    return asPath === '/data/download' || asPath === 'data/upload'
  }

  const restartAutoReset = () => {
    if (timeout) {
      clearTimeout(timeout)
    }

    timeout = setTimeout(
      async () => {
        await fetch('/api/oauth2/logout', { method: 'GET', credentials: 'include' })
      },
      isLongTimeout() ? 1800000 : 300000 // 30 mins and 5 mins respectively
    )
  }

  useEffect(() => {
    restartAutoReset()
    document.addEventListener('mousemove', restartAutoReset)
    document.addEventListener('mousedown', restartAutoReset)
    document.addEventListener('touchstart', restartAutoReset)
    document.addEventListener('click', restartAutoReset)
    document.addEventListener('keydown', restartAutoReset)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router.pathname])

  return (
    <ErrorBoundary FallbackComponent={ErrorBoundryComponent}>
      <CacheProvider value={emotionCache}>
        <ThemeProvider>
          <QueryClientProvider client={queryClient}>
            <style jsx global>
              {`
                body {
                  background-color: #fbfbfb;
                }
              `}
            </style>
            <Head>
              <title>rAPId</title>
            </Head>
            {getLayout(<Component {...pageProps} />)}
          </QueryClientProvider>
        </ThemeProvider>
      </CacheProvider>
    </ErrorBoundary>
  )
}
