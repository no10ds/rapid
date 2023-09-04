import {
  fireEvent,
  render,
  renderHook,
  RenderOptions,
  screen,
  waitFor
} from '@testing-library/react'
import { ThemeProvider } from '@/components'
import { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Dataset, PermissionUiResponse } from '@/service/types'

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
  const view = await render(wrapper(ui), options)
  return {
    ...view,
    rerender: (ui, options: Omit<RenderOptions, 'queries'> = {}) =>
      renderWithProviders(ui, { container: view.container, ...options })
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

export const mockDataset: Dataset = {
  layer: 'layer',
  domain: 'domain',
  dataset: 'dataset',
  version: 1
}

export const mockDataSetsList: Dataset[] = [
  {
    layer: 'layer',
    domain: 'Pizza',
    dataset: 'bit_complicated',
    version: 3
  },
  {
    layer: 'layer',
    domain: 'Pizza',
    dataset: 'again_complicated_high',
    version: 3
  },
  {
    layer: 'layer',
    domain: 'Apple',
    dataset: 'juicy',
    version: 2
  }
]

export const mockPermissionUiResponse: PermissionUiResponse = {
  DATA_ADMIN: 'DATA_ADMIN',
  USER_ADMIN: 'USER_ADMIN',
  READ: {
    ALL: {
      ALL: 'READ_ALL',
      PROTECTED: {
        TEST: 'READ_ALL_PROTECTED_TEST'
      }
    }
  },
  WRITE: {
    ALL: {
      ALL: 'WRITE_ALL',
      PROTECTED: {
        TEST: 'WRITE_ALL_PROTECTED_TEST'
      }
    },
    DEFAULT: {
      ALL: 'WRITE_DEFAULT_ALL',
      PROTECTED: {
        TEST: 'WRITE_DEFAULT_PROTECTED_TEST'
      }
    }
  }
}

export const selectAutocompleteOption = (id, value) => {
  const autocomplete = screen.getByTestId(id)
  const input = autocomplete.querySelector('input')
  autocomplete.focus()
  fireEvent.change(input, { target: { value: value } })
  fireEvent.keyDown(autocomplete, { key: 'ArrowDown' })
  fireEvent.keyDown(autocomplete, { key: 'Enter' })
  expect(input).toHaveValue(value)
}
