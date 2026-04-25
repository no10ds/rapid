import Link from 'next/link'

function FourOhFour() {
  return (
    <div className="error-boundary">
      <div className="error-boundary-card">
        <div className="error-boundary-title">Oops — Page not found</div>
        <Link href="/" className="btn-primary error-boundary-link">
          Go Home
        </Link>
      </div>
    </div>
  )
}

export default FourOhFour
