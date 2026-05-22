import { Chip } from '@mui/material'

const STATUS_PROPS: Record<string, { label: string; color: 'success' | 'warning' | 'error' }> = {
  SUCCESS: { label: 'Success', color: 'success' },
  'IN PROGRESS': { label: 'In Progress', color: 'warning' },
  FAILED: { label: 'Failed', color: 'error' }
}

const StatusChip = ({ status }: { status: string }) => {
  const props = STATUS_PROPS[status]
  return props ? (
    <Chip size="small" label={props.label} color={props.color} variant="outlined" />
  ) : (
    <Chip size="small" label={status} variant="outlined" />
  )
}

export default StatusChip
