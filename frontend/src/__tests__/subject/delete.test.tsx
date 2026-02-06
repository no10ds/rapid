import React from 'react'
import {
  screen,
  waitForElementToBeRemoved,
  waitFor,
  within
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import DeleteSubject from '@/pages/subject/delete/index'
import { renderWithProviders } from '@/utils/testing'

const mockData: Array<Record<string, string | undefined>> = [
  ...[...Array(2).keys()].map((i) => ({
    subject_id: `id_client_${i}`,
    subject_name: `client_title_${i}`,
    type: 'CLIENT'
  })),
  ...[...Array(2).keys()].map((i) => ({
    subject_id: `id_user_${i}`,
    subject_name: `user_title_${i}`,
    email: `${i}@example.com`,
    type: 'USER'
  }))
]

describe('DeleteSubject Component', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    renderWithProviders(<DeleteSubject />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    expect(screen.getByTestId('delete-button')).toBeInTheDocument()

    expect(fetchMock).toHaveBeenCalled()

    await waitFor(async () => {
      expect(
        within(screen.getByTestId('field-user')).getAllByRole('option')
      ).toHaveLength(mockData.length)
    })

    for (const { subject_id, subject_name } of mockData) {
      const option = screen.getByRole('option', { name: subject_name })
      expect(option).toBeInTheDocument()
      expect(option).toHaveValue(subject_id)
    }
  })

  it('handles error on fetch', async () => {
    const message = 'it broke'
    fetchMock.mockReject(new Error(message))
    renderWithProviders(<DeleteSubject />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    expect(screen.getByText(message)).toBeInTheDocument()
  })

  it('should show the confirmation dialog', async () => {
    const value = mockData[0].subject_name
    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    renderWithProviders(<DeleteSubject />)

    await waitFor(async () => {
      expect(
        within(screen.getByTestId('field-user')).getAllByRole('option')
      ).toHaveLength(mockData.length)
    })

    await userEvent.selectOptions(screen.getByTestId('field-user'), value)
    await userEvent.click(screen.getByTestId('delete-button'))

    await waitFor(async () => {
      expect(screen.getByTestId('delete-confirmation-dialog')).toBeInTheDocument()
    })
    expect(screen.getByTestId('delete-confirmation-dialog-delete-button')).toBeDisabled()
  })

  it('should delete a client', async () => {
    const value = mockData[0].subject_name
    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    renderWithProviders(<DeleteSubject />)

    await waitFor(async () => {
      expect(
        within(screen.getByTestId('field-user')).getAllByRole('option')
      ).toHaveLength(mockData.length)
    })

    await userEvent.selectOptions(screen.getByTestId('field-user'), value)
    await userEvent.click(screen.getByTestId('delete-button'))

    await waitFor(async () => {
      expect(screen.getByTestId('delete-confirmation-dialog')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByTestId('field-user-confirmation'), 'client_title_0')
    expect(screen.getByTestId('delete-confirmation-dialog-delete-button')).toBeEnabled()

    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    await userEvent.click(screen.getByTestId('delete-confirmation-dialog-delete-button'))

    await waitFor(async () => {
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/client/id_client_0',
        expect.objectContaining({
          method: 'DELETE'
        })
      )
    })
  })

  it('should delete a user', async () => {
    const value = mockData[2].subject_name
    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    renderWithProviders(<DeleteSubject />)

    await waitFor(async () => {
      expect(
        within(screen.getByTestId('field-user')).getAllByRole('option')
      ).toHaveLength(mockData.length)
    })

    await userEvent.selectOptions(screen.getByTestId('field-user'), value)
    await userEvent.click(screen.getByTestId('delete-button'))

    await waitFor(async () => {
      expect(screen.getByTestId('delete-confirmation-dialog')).toBeInTheDocument()
    })

    await userEvent.type(screen.getByTestId('field-user-confirmation'), 'user_title_0')
    expect(screen.getByTestId('delete-confirmation-dialog-delete-button')).toBeEnabled()

    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    await userEvent.click(screen.getByTestId('delete-confirmation-dialog-delete-button'))

    await waitFor(async () => {
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/user',
        expect.objectContaining({
          method: 'DELETE',
          body: JSON.stringify({ user_id: 'id_user_0', username: 'user_title_0' })
        })
      )
    })
  })
})
