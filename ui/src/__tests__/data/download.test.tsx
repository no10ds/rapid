import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import { mockDataSetsList, renderWithProviders } from '@/lib/test-utils'
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
    renderWithProviders(<DownloadPage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    const datasetDropdown = screen.getByTestId('select-dataset')
    expect(datasetDropdown).toBeVisible()

    for (const key in mockDataSetsList) {
      mockDataSetsList[key].forEach
      for (const { dataset } of mockDataSetsList[key]) {
        const option = within(datasetDropdown).getByRole('option', {
          name: dataset
        })
        expect(option).toBeInTheDocument()
        expect(option).toHaveValue(`${key}/${dataset}`)
      }
    }
  })

  it('renders version', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })

    renderWithProviders(<DownloadPage />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    await waitFor(async () => {
      expect(screen.getByTestId('select-version')).toBeInTheDocument()
    })
    ;[...Array(2).keys()].forEach((i) => {
      expect(
        within(screen.getByTestId('select-version')).getByRole('option', {
          name: (i + 1).toString()
        })
      ).toBeInTheDocument()
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

    renderWithProviders(<DownloadPage />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    await waitFor(async () => {
      expect(screen.getByTestId('select-version')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByTestId('submit'))

    await waitFor(async () => {
      expect(pushSpy).toHaveBeenCalledWith(
        `/data/download/Pizza/bit_complicated?version=3`
      )
    })
  })

  it('should display helper text when there is no data', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({}), { status: 200 })
    renderWithProviders(<DownloadPage />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    await waitFor(async () => {
      expect(screen.getByTestId('no-data-helper')).toBeInTheDocument()
    })
  })
})
