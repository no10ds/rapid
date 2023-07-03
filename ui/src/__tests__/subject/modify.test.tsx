import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import { renderWithProviders } from '@/lib/test-utils'
import SubjectModifyPage from '@/pages/subject/modify/index'

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

const pushSpy = jest.fn()
jest.mock('next/router', () => ({
  ...jest.requireActual('next/router'),
  useRouter: jest.fn(() => ({
    locale: 'en',
    push: pushSpy
  }))
}))

describe('Page: Subject Modify', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    renderWithProviders(<SubjectModifyPage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    expect(screen.getByTestId('field-user')).toBeInTheDocument()
    expect(screen.getByTestId('submit-button')).toBeInTheDocument()

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

  it('error on fetch', async () => {
    const message = 'it broke'
    fetchMock.mockReject(new Error(message))
    renderWithProviders(<SubjectModifyPage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    expect(screen.getByText(message)).toBeInTheDocument()
  })

  it('submits', async () => {
    const value = mockData[0].subject_name

    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    renderWithProviders(<SubjectModifyPage />)

    await waitFor(async () => {
      expect(
        within(screen.getByTestId('field-user')).getAllByRole('option')
      ).toHaveLength(mockData.length)
    })

    userEvent.selectOptions(screen.getByTestId('field-user'), value)

    fetchMock.mockResponseOnce(JSON.stringify(mockData), { status: 200 })
    await userEvent.click(screen.getByTestId('submit-button'))

    expect(pushSpy).toHaveBeenCalledWith({
      pathname: '/subject/modify/id_client_0',
      query: { name: value }
    })
  })
})
