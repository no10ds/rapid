import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import DeletePage from '@/pages/data/delete'
import { mockDataset, mockDataSetsList, renderWithProviders, selectAutocompleteOption } from '@/lib/test-utils'
import { DeleteDatasetResponse } from '@/service/types'

describe('Page: Delete page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
    renderWithProviders(<DeletePage datasetInput={mockDataset} />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    const datasetDropdown = screen.getByTestId('select-dataset')
    expect(datasetDropdown).toBeVisible()

    expect(screen.getByTestId('submit')).toBeInTheDocument()
  }
  )

  it('error on fetch', async () => {
    fetchMock.mockReject(new Error('fake error message'))
    renderWithProviders(<DeletePage datasetInput={mockDataset} />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    await waitFor(async () => {
      expect(screen.getByText('fake error message')).toBeInTheDocument()
    })
  })

  describe('on submit', () => {
    it('success', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
      renderWithProviders(<DeletePage datasetInput={mockDataset} />)

      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(fetchMock).toHaveBeenLastCalledWith(
          '/api/datasets/layer/domain/dataset',
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

      selectAutocompleteOption('select-layer', 'layer')
      selectAutocompleteOption('select-domain', 'Pizza')
      selectAutocompleteOption('select-dataset', 'bit_complicated')

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByTestId('delete-status')).toBeInTheDocument()
      })

      expect(
        screen.getByText('Dataset deleted: layer/Pizza/bit_complicated')
      ).toBeInTheDocument()
    })

    it('api error', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockDataSetsList), { status: 200 })
      renderWithProviders(<DeletePage datasetInput={mockDataset} />)

      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      fetchMock.mockReject(new Error('fake error message'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.getByText('fake error message')).toBeInTheDocument()
      })
    })
  })
})
