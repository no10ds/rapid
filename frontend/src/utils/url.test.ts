import { createUrl, isUrlInternal } from './url'

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

  it('url is only path', () => {
    expect(isUrlInternal('/someurl')).toBeTruthy()
    expect(isUrlInternal('/someurl?param=1')).toBeTruthy()
  })

  it('url contains full site', () => {
    expect(isUrlInternal(sitename, sitename)).toBeTruthy()
    expect(isUrlInternal(sitename + 'product/', sitename)).toBeTruthy()
    expect(isUrlInternal(sitename + '?param=1', sitename)).toBeTruthy()
  })

  it('throws error if invalid url', () => {
    expect(() => isUrlInternal('')).toThrow('Invalid URL:')
    expect(() => isUrlInternal('*^&*YH')).toThrow('Invalid URL:')
  })

  it('throws error if invalid currentUrl', () => {
    expect(() => isUrlInternal(sitename, '')).toThrow('Invalid URL:')
    expect(() => isUrlInternal(sitename, '*^&*YH')).toThrow('Invalid URL:')
  })

  it('url is external site', () => {
    expect(isUrlInternal('http://externalapp/', sitename)).toBeFalsy()
    expect(isUrlInternal('https://myapp/', sitename)).toBeFalsy()
  })
})
