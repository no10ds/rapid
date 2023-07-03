import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import fetchMock from 'jest-fetch-mock'
import { renderWithProviders } from '@/lib/test-utils'
import TasksPage from '@/pages/tasks/index'
import { AllJobsResponse } from '@/service/types'

const mockJobs: AllJobsResponse = [
  { status: 'SUCCESS' },
  { status: 'IN PROGRESS' },
  { status: 'FAILED' }
].map((data, i) => ({
  ...data,
  type: `type_${i}`,
  domain: `domain_${i}`,
  dataset: `dataset_${i}`,
  version: `version_${i}`,
  step: `step_${i}`,
  job_id: `job_id_${i}`
}))

describe('Page: Login page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('no data', async () => {
    fetchMock.mockResponseOnce(JSON.stringify([]))
    renderWithProviders(<TasksPage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    expect(screen.getByTestId('tasks-content')).toBeVisible()
  })

  it('renders with data', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockJobs))
    renderWithProviders(<TasksPage />)
    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    mockJobs.forEach((job) => {
      const link = screen.getByText(job.job_id as string)
      expect(screen.getByText(job.type as string)).toBeVisible()
      expect(screen.getByText(job.domain as string)).toBeVisible()
      expect(screen.getByText(job.dataset as string)).toBeVisible()
      expect(screen.getByText(job.version as string)).toBeVisible()

      expect(screen.getByText(job.step as string)).toBeVisible()
      expect(link).toBeVisible()
      expect(link).toHaveAttribute('href', `tasks/${job.job_id}`)
    })
    // screen.debug()

    expect(screen.getByText('Failure Details')).toBeVisible()
    expect(screen.getByText('Failure Details')).toHaveAttribute('href', `tasks/job_id_2`)
  })
})
