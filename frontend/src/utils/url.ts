export const createUrl = (
  url: RequestInfo | URL,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params?: string | URLSearchParams | Record<string, any> | string[][]
): string => {
  const queryString = new URLSearchParams(params).toString()
  return `${url}${queryString && `?${queryString}`}`
}

export const isUrlInternal = (
  url: string,
  currenSite = window.location.href
): boolean => {
  if (url.charAt(0) === '/') return true

  const fullUrl = new URL(url).origin
  const fullSite = new URL(currenSite).origin

  if (fullUrl === fullSite) return true
  return false
}
