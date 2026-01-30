import ThemeProvider from '../src/components/ThemeProvider'

export const parameters = {
  actions: { argTypesRegex: '^on[A-Z].*' },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/
    }
  },
  backgrounds: {
    options: {
      dark_grey: { name: 'Dark grey', value: '#AEAEAE' },
      light: { name: 'Light', value: '#E9EAEC' },
      white: { name: 'White', value: '#fff' }
    }
  }
}

export const decorators = [
  (Story) => (
    <ThemeProvider>
      <Story />
    </ThemeProvider>
  )
]

export const initialGlobals = {
  backgrounds: {
    value: 'white'
  }
};
