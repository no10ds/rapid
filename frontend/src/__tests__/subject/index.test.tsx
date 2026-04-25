import React from 'react'
import {
  screen,
  waitForElementToBeRemoved
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import SubjectIndex from '@/pages/subject/index'
import { renderWithProviders } from '@/utils/testing'

jest.mock('next/router', () => ({
  useRouter: () => ({ push: jest.fn(), query: {} })
}))

const subjects = [
  { subject_id: 'u1', subject_name: 'Alice', type: 'USER' },
  { subject_id: 'u2', subject_name: 'Bob', type: 'USER' },
  { subject_id: 'c1', subject_name: 'ClientOne', type: 'CLIENT' }
]

const permissions: Record<string, Array<Record<string, string | undefined>>> = {
  u1: [{ id: 'USER_ADMIN', type: 'USER_ADMIN' }],
  u2: [{ id: 'READ_ALL', type: 'READ', layer: 'ALL', sensitivity: 'ALL' }],
  c1: [{ id: 'WRITE_ALL', type: 'WRITE', layer: 'ALL', sensitivity: 'ALL' }]
}

function mockInitial() {
  fetchMock.mockResponse((req) => {
    if (req.url.endsWith('/api/subjects')) {
      return Promise.resolve(JSON.stringify(subjects))
    }
    const match = req.url.match(/\/api\/permissions\/(.+)$/)
    if (match) {
      return Promise.resolve(JSON.stringify(permissions[match[1]] ?? []))
    }
    return Promise.resolve('[]')
  })
}

describe('Subject index page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders all subjects with derived roles', async () => {
    mockInitial()
    renderWithProviders(<SubjectIndex />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
    expect(screen.getByText('ClientOne')).toBeInTheDocument()

    await screen.findByText('User Admin')
    expect(screen.getByText('Read Only')).toBeInTheDocument()
    expect(screen.getByText('Read/Write')).toBeInTheDocument()
  })

  it('filters by type', async () => {
    mockInitial()
    renderWithProviders(<SubjectIndex />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    await userEvent.click(screen.getByRole('button', { name: 'Clients' }))

    expect(screen.queryByText('Alice')).not.toBeInTheDocument()
    expect(screen.queryByText('Bob')).not.toBeInTheDocument()
    expect(screen.getByText('ClientOne')).toBeInTheDocument()
  })

  it('filters by search', async () => {
    mockInitial()
    renderWithProviders(<SubjectIndex />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    await userEvent.type(screen.getByPlaceholderText(/Search by name/i), 'Alice')

    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.queryByText('Bob')).not.toBeInTheDocument()
    expect(screen.queryByText('ClientOne')).not.toBeInTheDocument()
  })

  it('handles error on fetch', async () => {
    fetchMock.mockReject(new Error('boom'))
    renderWithProviders(<SubjectIndex />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    expect(screen.getByText('boom')).toBeInTheDocument()
  })
})
