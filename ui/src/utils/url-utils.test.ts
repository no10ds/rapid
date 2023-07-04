import { createUrl, isUrlInternal } from './url-utils'

describe('createUrl()', () => {
  it('returns url with querystring', () => {
    expect(createUrl('/path', { food: 'pizza', fruit: 'apple' })).toEqual(
      '/path?food=pizza&fruit=apple'
    )

    expect(createUrl('/path', { food: ['pizza', 'chips'], fruit: 'apple' })).toEqual(
      '/path?food=pizza%2Cchips&fruit=apple'
    )
  })

  it('empty params', () => {
    expect(createUrl('/path', {})).toEqual('/path')
    expect(createUrl('/path')).toEqual('/path')
  })
})

describe('isUrlInternal()', () => {
  const sitename = 'http://myapp/'
  const { location } = window

  beforeAll(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    delete (window as any).location
  })

  afterAll(() => {
    window.location = location
  })

  beforeEach(() => {
    window.location = {
      ...location,
      href: sitename
    }
  })

  it('url is only path', () => {
    expect(isUrlInternal('/someurl')).toBeTruthy()
    expect(isUrlInternal('/someurl?param=1')).toBeTruthy()
  })

  it('url contains full site', () => {
    expect(isUrlInternal(sitename)).toBeTruthy()
    expect(isUrlInternal(sitename + 'product/')).toBeTruthy()
    expect(isUrlInternal(sitename + '?param=1')).toBeTruthy()
  })

  it('throws error if invalid url', () => {
    expect(() => isUrlInternal('')).toThrowError('Invalid URL:')
    expect(() => isUrlInternal('*^&*YH')).toThrowError('Invalid URL:')
  })

  it('throws error if invalid currentUrl', () => {
    expect(() => isUrlInternal(sitename, '')).toThrowError('Invalid URL:')
    expect(() => isUrlInternal(sitename, '*^&*YH')).toThrowError('Invalid URL:')
  })

  it('url is external site', () => {
    expect(isUrlInternal('http://externalapp/')).toBeFalsy()
    expect(isUrlInternal('https://myapp/')).toBeFalsy()
  })
})
