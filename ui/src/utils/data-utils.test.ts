import { api } from './data-utils'
import fetchMock from 'jest-fetch-mock'
import { defaultError } from '@/lang'

const mockSuccess = { fruit: 'apples' }

describe('api()', () => {
  afterEach(() => {
    fetchMock.resetMocks()
  })

  it('success', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockSuccess), { status: 200 })
    const data = await (await api('/api')).json()
    expect(data).toEqual(expect.objectContaining(mockSuccess))
  })

  it('default error', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(mockSuccess), { status: 401 })

    try {
      await api('/api')
    } catch (e) {
      expect(e.message).toEqual(defaultError)
    }
  })

  it('custom error', async () => {
    const errorMessage = 'my custom error'

    fetchMock.mockResponseOnce(JSON.stringify({ details: 'my custom error' }), {
      status: 401
    })

    try {
      await api('/api')
    } catch (e) {
      expect(e.message).toEqual(errorMessage)
    }
  })
})
