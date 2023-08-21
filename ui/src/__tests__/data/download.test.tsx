import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import { mockDataset, mockDataSetsList, renderWithProviders } from '@/lib/test-utils'
import DownloadPage from '@/pages/data/download/'

const pushSpy = jest.fn()
jest.mock('next/router', () => ({
  ...jest.requireActual('next/router'),
  useRouter: jest.fn(() => ({
    locale: 'en',
    push: pushSpy
  }))
}))

describe('Page: Download page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders dataset drodown', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
    renderWithProviders(<DownloadPage datasetInput={mockDataset} />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    const datasetDropdown = screen.getByTestId('select-dataset')
    expect(datasetDropdown).toBeVisible()

    expect(screen.getByTestId('submit')).toBeInTheDocument()
  }
  )

  it('renders dataset-selector', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })

    renderWithProviders(<DownloadPage datasetInput={mockDataset} />)

    await waitFor(async () => {
      expect(screen.getByTestId('select-layer')).toBeInTheDocument()
    })
  })

  it('fetch error', async () => {
    fetchMock.mockReject(new Error('fake error message'))

    renderWithProviders(<DownloadPage />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    expect(screen.getByText('fake error message')).toBeInTheDocument()
  })

  it('on submit', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })

    renderWithProviders(<DownloadPage datasetInput={mockDataset} />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    await userEvent.click(screen.getByTestId('submit'))

    await waitFor(async () => {
      expect(pushSpy).toHaveBeenCalledWith(
        `/data/download/layer/domain/dataset?version=1`
      )
    })
  })

  it('should display helper text when there is no data', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({}), { status: 200 })
    renderWithProviders(<DownloadPage datasetInput={mockDataset} />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    await waitFor(async () => {
      expect(screen.getByTestId('no-data-helper')).toBeInTheDocument()
    })
  })
})
