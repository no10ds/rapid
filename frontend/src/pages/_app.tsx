import { ThemeProvider } from '@/components'
import { CacheProvider, EmotionCache } from '@emotion/react'
import createEmotionCache from '@/utils/createEmotionCache'
import { ErrorBoundary } from 'react-error-boundary'
import { ReactNode, useEffect, useRef } from 'react'
import { AppProps } from 'next/app'
import { NextPage } from 'next'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import Head from 'next/head'
import { useRouter } from 'next/router'
import ErrorBoundryComponent from '@/components/ErrorBoundryComponent'
import '@/style/globals.css'

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

const ACTIVITY_EVENTS = ['mousemove', 'mousedown', 'touchstart', 'click', 'keydown'] as const

export default function MyApp({
  Component,
  emotionCache = clientSideEmotionCache,
  pageProps
}: MyAppProps) {
  const router = useRouter()
  const { asPath } = router
  const getLayout = Component.getLayout ?? ((page) => page)

  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const isLongTimeout = asPath === '/data/download' || asPath === '/data/upload'

    const restartAutoReset = () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(
        async () => {
          await fetch('/api/oauth2/logout', { method: 'GET', credentials: 'include' })
        },
        isLongTimeout ? 1800000 : 300000
      )
    }

    restartAutoReset()
    ACTIVITY_EVENTS.forEach((e) => document.addEventListener(e, restartAutoReset))

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      ACTIVITY_EVENTS.forEach((e) => document.removeEventListener(e, restartAutoReset))
    }
  }, [asPath])

  return (
    <CacheProvider value={emotionCache}>
      <ThemeProvider>
        <ErrorBoundary FallbackComponent={ErrorBoundryComponent}>
          <QueryClientProvider client={queryClient}>
            <Head>
              <title>rAPId</title>
            </Head>
            {getLayout(<Component {...pageProps} />)}
            <ReactQueryDevtools initialIsOpen={false} />
          </QueryClientProvider>
        </ErrorBoundary>
      </ThemeProvider>
    </CacheProvider>
  )
}
