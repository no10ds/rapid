import {
  fireEvent,
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import DeletePage from '@/pages/data/delete'
import { mockDataSetsList, renderWithProviders } from '@/lib/test-utils'
import { DeleteDatasetResponse } from '@/service/types'

describe('Page: Delete page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
    renderWithProviders(<DeletePage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    const datasetDropdown = screen.getByTestId('select-dataset')
    expect(datasetDropdown).toBeVisible()

    for (const key in mockDataSetsList) {
      mockDataSetsList[key].forEach
      for (const { dataset } of mockDataSetsList[key]) {
        const option = within(datasetDropdown).getByRole('option', { name: dataset })
        expect(option).toBeInTheDocument()
        expect(option).toHaveValue(`${key}/${dataset}`)
      }
    }
  })

  it('error on fetch', async () => {
    fetchMock.mockReject(new Error('fake error message'))
    renderWithProviders(<DeletePage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    await waitFor(async () => {
      expect(screen.getByText('fake error message')).toBeInTheDocument()
    })
  })

  describe('on submit', () => {
    it('success', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
      renderWithProviders(<DeletePage />)

      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      userEvent.selectOptions(
        screen.getByTestId('select-dataset'),
        mockDataSetsList['Pizza'][0].dataset
      )

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(fetchMock).toHaveBeenLastCalledWith(
          '/api/datasets/Pizza/bit_complicated',
          expect.objectContaining({
            credentials: 'include',
            method: 'DELETE'
          })
        )
      })
    })

    it('delete status', async () => {
      const mockSuccess: DeleteDatasetResponse = {
        details: 'dataset successfully deleted'
      }

      fetchMock.mockResponses(
        [JSON.stringify(mockDataSetsList), { status: 200 }],
        [JSON.stringify(mockSuccess), { status: 200 }]
      )
      renderWithProviders(<DeletePage />)
      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByTestId('delete-status')).toBeInTheDocument()
      })

      expect(
        screen.getByText('Dataset deleted: Pizza/bit_complicated')
      ).toBeInTheDocument()
    })

    it('api error', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
      renderWithProviders(<DeletePage />)

      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      fetchMock.mockReject(new Error('fake error message'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByText('fake error message')).toBeInTheDocument()
      })
    })
  })
})
