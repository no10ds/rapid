import { screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react'
import fetchMock from 'jest-fetch-mock'
import { renderWithProviders } from '@/lib/test-utils'
import LoginPage from '@/pages/login'
import { AuthResponse, GetLoginResponse } from '@/service/types'

const mockAuth: AuthResponse = { detail: 'success' }
const mockLogin: GetLoginResponse = { auth_url: 'http://my-apiurl/' }

const replaceSpy = jest.fn()
jest.mock('next/router', () => ({
  ...jest.requireActual('next/router'),
  useRouter: jest.fn(() => ({
    locale: 'en',
    replace: replaceSpy
  }))
}))

describe('Page: Login page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders after preloader', async () => {
    renderWithProviders(<LoginPage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))
    const link = screen.getByTestId('login-link')
    expect(link).toBeVisible()
    expect(link).toHaveAttribute('href', '/login')
  })

  it('on valid auth redirects', async () => {
    fetchMock.mockResponses(
      [JSON.stringify(mockAuth), { status: 200 }],
      [JSON.stringify(mockLogin), { status: 200 }]
    )
    renderWithProviders(<LoginPage />)
    await waitFor(async () => {
      expect(replaceSpy).toHaveBeenCalledWith({
        pathname: '/'
      })
    })
    expect(screen.getByTestId('login-link')).toHaveAttribute('href', mockLogin.auth_url)
  })

  it.skip('on error', () => jest.fn())
})
