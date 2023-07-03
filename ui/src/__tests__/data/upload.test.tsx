import {
  fireEvent,
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import { mockDataSetsList, renderWithProviders } from '@/lib/test-utils'
import UploadPage from '@/pages/data/upload'
import { UploadDatasetResponse } from '@/service/types'

const pushSpy = jest.fn()
jest.mock('next/router', () => ({
  ...jest.requireActual('next/router'),
  useRouter: jest.fn(() => ({
    locale: 'en',
    push: pushSpy
  }))
}))

describe('Page: Upload page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
    renderWithProviders(<UploadPage />)

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

    expect(screen.getByTestId('upload')).toBeInTheDocument()
  })

  it('error on fetch', async () => {
    fetchMock.mockReject(new Error('fake error message'))
    renderWithProviders(<UploadPage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    await waitFor(async () => {
      expect(screen.getByText('fake error message')).toBeInTheDocument()
    })
  })

  describe('on submit', () => {
    const file = new File(['test'], 'testfile.txt', { type: 'text/plain' })

    it('success', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
      renderWithProviders(<UploadPage />)

      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      await fireEvent.change(screen.getByTestId('upload'), {
        target: { files: [file] }
      })

      userEvent.selectOptions(
        screen.getByTestId('select-dataset'),
        mockDataSetsList['Pizza'][0].dataset
      )

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(fetchMock).toHaveBeenLastCalledWith(
          '/api/datasets/Pizza/bit_complicated',
          expect.objectContaining({
            body: new FormData(),
            credentials: 'include',
            method: 'POST'
          })
        )
      })
    })

    it('upload status failure', async () => {
      const mockSuccess: UploadDatasetResponse = {
        details: {
          dataset_version: 12314,
          job_id: 'abc123',
          original_filename: 'my_original_name.txt',
          raw_filename: 'my_raw_name.txt',
          status: 'winning'
        }
      }

      fetchMock.mockResponses(
        [JSON.stringify(mockDataSetsList), { status: 200 }],
        [JSON.stringify(mockSuccess), { status: 200 }],
        [JSON.stringify({ status: "FAILED" }), { status: 200 }]
      )
      renderWithProviders(<UploadPage />)
      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByTestId('upload-status')).toBeInTheDocument()
      })

      await waitFor(async () => {
        const trackLink = screen.getByText('See error details')
        expect(trackLink).toHaveAttribute('href', '/tasks/abc123')
      })

      await waitFor(async () => {
        expect(screen.getByText('Status: Data upload error')).toBeInTheDocument()
      })
    })

    it('upload status success', async () => {
      const mockSuccess: UploadDatasetResponse = {
        details: {
          dataset_version: 12314,
          job_id: 'abc123',
          original_filename: 'my_original_name.txt',
          raw_filename: 'my_raw_name.txt',
          status: 'winning'
        }
      }

      fetchMock.mockResponses(
        [JSON.stringify(mockDataSetsList), { status: 200 }],
        [JSON.stringify(mockSuccess), { status: 200 }],
        [JSON.stringify({ status: "SUCCESS" }), { status: 200 }]
      )
      renderWithProviders(<UploadPage />)
      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByTestId('upload-status')).toBeInTheDocument()
      })

      await waitFor(async () => {
        const trackLink = screen.getByText('See upload details')
        expect(trackLink).toHaveAttribute('href', '/tasks/abc123')
      })

      await waitFor(async () => {
        expect(screen.getByText('Status: Data uploaded successfully')).toBeInTheDocument()
      })
    })

    it('upload status in progress', async () => {
      const mockSuccess: UploadDatasetResponse = {
        details: {
          dataset_version: 12314,
          job_id: 'abc123',
          original_filename: 'my_original_name.txt',
          raw_filename: 'my_raw_name.txt',
          status: 'winning'
        }
      }

      fetchMock.mockResponses(
        [JSON.stringify(mockDataSetsList), { status: 200 }],
        [JSON.stringify(mockSuccess), { status: 200 }],
        [JSON.stringify({ status: "IN PROGRESS" }), { status: 200 }]
      )
      renderWithProviders(<UploadPage />)
      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByTestId('upload-status')).toBeInTheDocument()
      })

      const trackLink = screen.getByText('See progress details')

      expect(trackLink).toBeInTheDocument()
      expect(trackLink).toHaveAttribute('href', '/tasks/abc123')
      await waitFor(async () => {
        expect(screen.getByText('Status: Data processing')).toBeInTheDocument()
      })
    })


    it('api error', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
      renderWithProviders(<UploadPage />)

      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      fetchMock.mockReject(new Error('fake error message'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByText('fake error message')).toBeInTheDocument()
      })
    })
  })
})
