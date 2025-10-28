import Alert from '../Alert/Alert'
import Card from '../Card/Card'

type Props = {
  error: Error
}

const ErrorCard = ({ error }: Props) => {
  return error ? (
    <Card>
      <Alert severity="error" sx={{ mb: 3 }}>
        {error.message}
      </Alert>
    </Card>
  ) : null
}

export default ErrorCard
