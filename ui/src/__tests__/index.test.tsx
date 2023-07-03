import { screen, waitFor } from '@testing-library/react'
import fetchMock from 'jest-fetch-mock'
import { renderWithProviders } from '@/lib/test-utils'
import IndexPage from '@/pages/index'
import { MethodsResponse } from '@/service/types'

describe('Page: Index page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
  })

  it('preloader', async () => {
    renderWithProviders(<IndexPage />)

    expect(screen.getByRole('progressbar')).toBeVisible()
  })

  describe('permissions', () => {
    const mockData: MethodsResponse = {
      can_manage_users: false,
      can_upload: false,
      can_download: false,
      can_create_schema: false,
      can_search_catalog: false,
      message: 'some error message'
    }

    it('none', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockData))
      renderWithProviders(<IndexPage />)

      await waitFor(async () =>
        expect(screen.getByText('Welcome to rAPId')).toBeVisible()
      )

      expect(screen.getByTestId('intro')).toBeVisible()

      expect(screen.queryByTestId('user-management')).not.toBeInTheDocument()
      expect(screen.queryByTestId('data-management')).not.toBeInTheDocument()
      expect(screen.queryByTestId('schema-management')).not.toBeInTheDocument()
      expect(screen.queryByTestId('task-status')).not.toBeInTheDocument()
    })

    it('User Management', async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ ...mockData, can_manage_users: true }))
      renderWithProviders(<IndexPage />)

      await waitFor(async () =>
        expect(screen.getByTestId('user-management')).toBeVisible()
      )

      expect(screen.queryByTestId('data-management')).not.toBeInTheDocument()
      expect(screen.queryByTestId('schema-management')).not.toBeInTheDocument()
      expect(screen.queryByTestId('task-status')).not.toBeInTheDocument()
    })

    it('Data Management', async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ ...mockData, can_upload: true }))
      renderWithProviders(<IndexPage />)

      await waitFor(async () =>
        expect(screen.getByTestId('data-management')).toBeVisible()
      )
      expect(screen.getByTestId('task-status')).toBeInTheDocument()
      expect(screen.queryByTestId('user-management')).not.toBeInTheDocument()
      expect(screen.queryByTestId('schema-management')).not.toBeInTheDocument()
    })

    it('Data Management for downloading data', async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ ...mockData, can_download: true }))
      renderWithProviders(<IndexPage />)

      await waitFor(async () =>
        expect(screen.getByTestId('data-management')).toBeVisible()
      )
      expect(screen.getByTestId('task-status')).toBeInTheDocument()
      expect(screen.queryByTestId('user-management')).not.toBeInTheDocument()
      expect(screen.queryByTestId('schema-management')).not.toBeInTheDocument()
    })

    it('Schema Management', async () => {
      fetchMock.mockResponseOnce(
        JSON.stringify({ ...mockData, can_upload: true, can_create_schema: true })
      )
      renderWithProviders(<IndexPage />)

      await waitFor(async () =>
        expect(screen.getByTestId('data-management')).toBeVisible()
      )
      expect(screen.getByTestId('schema-management')).toBeVisible()
      expect(screen.getByTestId('task-status')).toBeInTheDocument()

      expect(screen.queryByTestId('user-management')).not.toBeInTheDocument()
    })
  })
})
