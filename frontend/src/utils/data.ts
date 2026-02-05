import { createUrl } from './url'
import { defaultError } from '@/lang'
import { getDevToken } from '@/service'

export type ParamsType = Record<string, string | string[] | number>

export const api = async (
  path: RequestInfo | URL,
  init: RequestInit = {},
  params?: ParamsType
): Promise<Response> => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL
  const baseUrl = API_URL ? `${API_URL}${path}` : path
  const url = createUrl(`${baseUrl}`, params)
  let detailMessage

  let headers = init.headers || {}

  if (process.env.NODE_ENV === 'development') {
    const response = await getDevToken()
    headers['Authorization'] = `Bearer ${response.token}`
  }

  // Don't set Content-Type for FormData (file uploads)
  if (!(init.body instanceof FormData)) {
    headers = { ...headers, 'Content-Type': 'application/json' }
  }

  const res: Response = await fetch(url, {
    credentials: 'include',
    ...init,
    headers
  })
  if (res.ok) return res
  try {
    const { details } = await res.json()
    detailMessage = details
  } catch {
    // Ignore JSON parsing errors
  }
  throw new Error(detailMessage || defaultError)
}
