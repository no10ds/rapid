import { createUrl } from './url-utils'
import { defaultError } from '@/lang'

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
  const res: Response = await fetch(url, {
    credentials: 'include',
    ...init
  })
  if (res.ok) return res
  try {
    const { details } = await res.json()
    detailMessage = details
  } catch (e) {}
  throw new Error(detailMessage || defaultError)
}
