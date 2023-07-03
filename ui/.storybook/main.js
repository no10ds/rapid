const path = require('path')

module.exports = {
  stories: [
    '../src/components/**/*.stories.mdx',
    '../src/components/**/*.stories.@(js|jsx|ts|tsx)'
  ],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    'storybook-addon-designs',
    '@storybook/addon-a11y'
  ],
  framework: '@storybook/react',
  staticDirs: ['../public'],
  core: {
    builder: '@storybook/builder-webpack5',
    disableTelemetry: true
  },
  typescript: {
    check: true
  },
  features: {
    emotionAlias: false
  },
  webpackFinal: async (config, { configType }) => {
    config.resolve.modules = [path.resolve(__dirname, '..'), 'node_modules']
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, '../src/')
    }
    return config
  }
}
