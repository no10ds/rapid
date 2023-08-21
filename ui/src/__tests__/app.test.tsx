import fetchMock from 'jest-fetch-mock'
import { renderWithProviders } from '@/lib/test-utils'
import AppPage from '@/pages/_app'

jest.useFakeTimers()
jest.spyOn(global, 'setTimeout')

describe('Page: App page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
  })

  it('timeout ', async () => {
    renderWithProviders(
      <AppPage Component={jest.fn()} pageProps={undefined} router={null} />
    )
    expect(setTimeout).toHaveBeenCalledTimes(1)
    expect(setTimeout).toHaveBeenLastCalledWith(expect.any(Function), 300000)

    jest.runOnlyPendingTimers()

    expect(fetchMock).toBeCalledWith('/api/oauth2/logout', {
      credentials: 'include',
      method: 'GET'
    })
  })
})
