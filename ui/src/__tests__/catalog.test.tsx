import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import fetchMock from 'jest-fetch-mock'
import { renderWithProviders } from '@/utils/testing'
import CatalogPage from '@/pages/catalog/[search]'
import { MetadataSearchResponse } from '@/service/types'

const searchSpy = jest.fn()
jest.mock('next/router', () => ({
  ...jest.requireActual('next/router'),
  useRouter: jest.fn(() => ({
    locale: 'en',
    query: { search: searchSpy }
  }))
}))

const mockMetadataSearchResponse: MetadataSearchResponse = [
  {
    matching_data: 'mock_data',
    matching_field: 'columns',
    dataset: 'dataset',
    domain: 'domain',
    version: '1'
  }
]

describe('Page: Catalog page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('no data', async () => {
    fetchMock.mockResponseOnce(JSON.stringify([]))
    renderWithProviders(<CatalogPage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    expect(screen.getByTestId('empty-search-content')).toBeVisible()
  })

  it('renders with data', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockMetadataSearchResponse))
    renderWithProviders(<CatalogPage />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    mockMetadataSearchResponse.forEach((item) => {
      expect(screen.getByText(item.domain)).toBeVisible()
      expect(screen.getByText(item.dataset)).toBeVisible()
      expect(screen.getByText(item.version)).toBeVisible()
      expect(screen.getByText(item.matching_data)).toBeVisible()
      expect(screen.getByText('Column')).toBeVisible()
    })
  })
})
