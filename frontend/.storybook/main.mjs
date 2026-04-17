import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default {
  stories: [
    '../src/components/**/*.stories.@(js|jsx|ts|tsx)'
  ],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-a11y',
    '@storybook/addon-docs'
  ],
  framework: {
    name: '@storybook/nextjs-vite',
    options: {}
  },
  staticDirs: ['../public'],
  core: {
    disableTelemetry: true
  },
  typescript: {
    check: true
  },
  viteFinal: async (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, '../src/')
    }
    return config
  }
}
