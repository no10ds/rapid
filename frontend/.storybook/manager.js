import { addons } from 'storybook/manager-api'
import theme from './theme'

addons.setConfig({
  showPanel: true,
  panelPosition: 'bottom',
  theme
})
