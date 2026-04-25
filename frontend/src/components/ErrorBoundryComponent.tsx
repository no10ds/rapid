import Link from 'next/link'

function ErrorBoundryComponent() {
  return (
    <div className="error-boundary">
      <div className="error-boundary-card">
        <div className="error-boundary-title">Oops — Something Went Wrong</div>
        <p className="error-boundary-body">
          If this is a regular occurrence with the application please get in touch or
          raise a ticket.
        </p>
        <Link href="/" className="btn-primary error-boundary-link">
          Go Home
        </Link>
      </div>
    </div>
  )
}

export default ErrorBoundryComponent
