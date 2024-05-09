/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-var-requires */
// Optional: configure or set up a testing framework before each test.
// If you delete this file, remove `setupFilesAfterEnv` from `jest.config.js`

// Used for __tests__/testing-library.js
// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'
import '@testing-library/jest-dom/extend-expect'
import { TextDecoder, TextEncoder } from 'util'
global.TextEncoder = TextEncoder
;(global as any).TextDecoder = TextDecoder

require('jest-fetch-mock').enableMocks()

jest.mock('next/config', () => () => ({
  publicRuntimeConfig: {
    apiUrl: 'http://myapp'
  }
}))

jest.mock('next/router', () => ({
  ...jest.requireActual('next/router'),
  useRouter: jest.fn(() => ({ locale: 'en', push: jest.fn(), replace: jest.fn() }))
}))
