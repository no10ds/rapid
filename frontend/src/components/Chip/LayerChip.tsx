import { Chip } from '@mui/material'

type LayerColor = 'info' | 'success' | 'warning' | 'default'

function layerColor(layer: string): LayerColor {
  switch (layer?.toLowerCase()) {
    case 'raw': return 'info'
    case 'curated': return 'success'
    case 'processed': return 'warning'
    default: return 'default'
  }
}

const LayerChip = ({ layer }: { layer: string }) => (
  <Chip size="small" label={layer} color={layerColor(layer)} variant="outlined" />
)

export default LayerChip
