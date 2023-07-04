import { render, renderHook, RenderOptions, waitFor } from '@testing-library/react'
import { ThemeProvider } from '@/components'
import { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

beforeAll(() => {
  Object.defineProperty(global, 'sessionStorage', { value: mockStorage })
  Object.defineProperty(global, 'localStorage', { value: mockStorage })
  jest.spyOn(console, 'error').mockImplementation(jest.fn())
})

afterEach(() => {
  window.sessionStorage.clear()
})

const mockStorage = (() => {
  let store = {}
  return {
    getItem: function (key) {
      return store[key] || null
    },
    setItem: function (key, value) {
      store[key] = value.toString()
    },
    removeItem: function (key) {
      delete store[key]
    },
    clear: function () {
      store = {}
    }
  }
})()

export const wrapper = (ui) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false
      }
    }
  })
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <>{ui}</>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export const renderWithProviders = async (
  ui: ReactNode,
  options: Omit<RenderOptions, 'queries'> = {}
) => {
  const rendered = await render(wrapper(ui), options)
  return {
    ...rendered,
    rerender: (ui, options: Omit<RenderOptions, 'queries'> = {}) =>
      renderWithProviders(ui, { container: rendered.container, ...options })
  }
}

export const renderHookWithProviders: typeof renderHook = (...parameters) =>
  renderHook(parameters[0], {
    wrapper: ({ children }) => wrapper(children),
    ...parameters[1]
  })

export const bugfixForTimeout = async () =>
  await waitFor(() => new Promise((resolve) => setTimeout(resolve, 0)))

export * from '@testing-library/react'
export { renderWithProviders as render }

export const mockDataSetsList: { [key: string]: { [key: string]: string }[] } = {
  Pizza: [
    {
      dataset: 'bit_complicated',
      version: '3'
    },
    {
      dataset: 'again_complicated_high',
      version: '3'
    }
  ],
  Apples: [
    {
      dataset: 'juicy',
      version: '2'
    }
  ]
}
