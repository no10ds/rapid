import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getJob } from '@/service'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { ReactNode } from 'react'
import Link from 'next/link'

function getStatusBadge(status: string) {
  if (status === 'SUCCESS')
    return <span className="badge ok"><span className="bdot" />Success</span>
  if (status === 'IN PROGRESS')
    return <span className="badge pnd"><span className="bdot" />In Progress</span>
  if (status === 'FAILED')
    return <span className="badge err"><span className="bdot" />Failed</span>
  return <span className="badge">{status}</span>
}

function formatTs(ts: number | string | undefined): string | null {
  if (!ts) return null
  const n = typeof ts === 'string' ? parseInt(ts, 10) : ts
  if (!n || isNaN(n)) return null
  return new Date(n * 1000).toLocaleString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

type ParsedError = {
  title: string
  detail: string
}

function parseError(raw: string): ParsedError {
  // Expected columns: [...], received: [...]
  const colMismatch = raw.match(/Expected columns:\s*(\[[\s\S]*?\]),\s*received:\s*(\[[\s\S]*?\])/)
  if (colMismatch) {
    return {
      title: 'Column mismatch — your file does not match the schema',
      detail: `The schema expects columns ${colMismatch[1]} but your file contains ${colMismatch[2]}. Check that all required columns are present and no extra columns have been added.`
    }
  }

  // Column [X] does not match specified date format in at least one row
  const dateFormat = raw.match(/Column \[(.+?)\] does not match specified date format/)
  if (dateFormat) {
    return {
      title: `Invalid date format in column "${dateFormat[1]}"`,
      detail: `At least one value in the "${dateFormat[1]}" column does not match the date format required by the schema. Check that all dates in this column are consistently formatted.`
    }
  }

  // Column [X] has an incorrect data type. Expected Y, received Z
  const dataType = raw.match(/Column \[(.+?)\] has an incorrect data type\. Expected (.+?), received (.+)/)
  if (dataType) {
    return {
      title: `Wrong data type in column "${dataType[1]}"`,
      detail: `The schema expects "${dataType[1]}" to contain ${dataType[2]} values, but your file contains ${dataType[3]} values. Check that the column contains the correct type of data.`
    }
  }

  // Partition column [X] has values with illegal characters '/'
  const partition = raw.match(/Partition column \[(.+?)\] has values with illegal characters/)
  if (partition) {
    return {
      title: `Illegal character in partition column "${partition[1]}"`,
      detail: `Values in the "${partition[1]}" column contain a "/" character, which is not allowed in partition columns. Remove or replace any forward slashes in this column.`
    }
  }

  // Dataset has no rows
  if (/dataset has no rows/i.test(raw)) {
    return {
      title: 'File contains no data rows',
      detail: 'Your file appears to be empty or contains only a header row. Make sure your file has at least one data row before uploading.'
    }
  }

  // Pandera not_nullable — column X
  const nullable = raw.match(/column\s*['""]?(.+?)['""]?\s+.*?null/i)
  if (nullable && /null/i.test(raw)) {
    const col = nullable[1].replace(/['"]/g, '').trim()
    return {
      title: `Missing values found in column "${col}"`,
      detail: `The "${col}" column has empty or null values, but the schema requires this column to always have a value. Fill in any blank cells in this column before re-uploading.`
    }
  }

  // Pandera uniqueness — column X
  if (/unique/i.test(raw)) {
    const colMatch = raw.match(/column\s+['""]?(.+?)['""]?[\s,]/i)
    const col = colMatch ? colMatch[1].replace(/['"]/g, '').trim() : 'a column'
    return {
      title: `Duplicate values found in column "${col}"`,
      detail: `The "${col}" column must contain unique values, but duplicate entries were found. Remove duplicates before re-uploading.`
    }
  }

  // Fallback — clean up common technical noise but show original
  return {
    title: 'Validation error',
    detail: raw
  }
}

function GetJob() {
  const router = useRouter()
  const { jobId } = router.query
  const { isLoading, data, error } = useQuery(['getJob', jobId], getJob)

  if (isLoading) return <div className="rapid-loading-bar" role="progressbar" />
  if (error) return <ErrorCard error={error as Error} />

  const errors: string[] = Array.isArray(data.errors)
    ? (data.errors as string[])
    : data.errors
      ? [String(data.errors)]
      : []

  const parsedErrors = errors.map(parseError)
  const hasFailed = data.status === 'FAILED'
  const createdAtStr = formatTs(data.createdat as number | string | undefined)

  const metaRows: [string, ReactNode][] = [
    ['Job ID', <span key="id" style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, userSelect: 'all' }}>{data.job_id as string}</span>],
    ['Type', data.type as string],
    ...(data.filename ? [['File', <span key="fn" style={{ fontFamily: "'DM Mono', monospace", fontSize: 12 }}>{data.filename as string}</span>] as [string, ReactNode]] : []),
    ['Dataset', `${data.domain} / ${data.dataset}`],
    ['Layer', data.layer as string],
    ['Version', String(data.version)],
    ...(createdAtStr ? [['Started', createdAtStr] as [string, ReactNode]] : []),
  ]

  return (
    <div style={{ maxWidth: 860, margin: '0 auto' }}>
      {/* Job detail card */}
      <div className="form-card" style={{ marginBottom: 16 }}>
        <div className="form-card-hd">
          <div className="form-card-title">Job Detail</div>
          <div style={{ marginLeft: 'auto' }}>
            {getStatusBadge(data.status as string)}
          </div>
        </div>
        <div className="form-card-body" style={{ padding: 0 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              {metaRows.map(([k, v]) => (
                <tr key={k as string} style={{ borderBottom: '1px solid #f4f4f5' }}>
                  <td style={{
                    width: 140, padding: '9px 20px',
                    fontSize: 11, fontWeight: 600,
                    color: 'var(--text-tertiary)',
                    textTransform: 'uppercase',
                    letterSpacing: '.04em',
                    whiteSpace: 'nowrap'
                  }}>
                    {k}
                  </td>
                  <td style={{ padding: '9px 20px', fontSize: 13 }}>{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Errors card */}
      {hasFailed && parsedErrors.length > 0 && (
        <div className="form-card" style={{ borderColor: '#fecaca' }}>
          <div className="form-card-hd" style={{ background: '#fef2f2', borderBottomColor: '#fecaca', gap: 10 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <div className="form-card-title" style={{ color: '#dc2626' }}>
                {parsedErrors.length === 1 && parsedErrors[0].title !== 'Validation error'
                  ? parsedErrors[0].title
                  : "Your file didn't pass validation"}
              </div>
              <div style={{ fontSize: 12, color: '#b91c1c' }}>
                No data was written. Fix the issues below, then re-upload.
              </div>
            </div>
            <div style={{ marginLeft: 'auto', fontSize: 11, color: '#b91c1c', fontWeight: 600, whiteSpace: 'nowrap' }}>
              {parsedErrors.length} error{parsedErrors.length !== 1 ? 's' : ''}
            </div>
          </div>

          <div className="form-card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* Error list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {parsedErrors.map((e, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 10, alignItems: 'flex-start',
                  padding: '10px 12px',
                  background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 6
                }}>
                  <span style={{ color: '#dc2626', fontSize: 13, flexShrink: 0, marginTop: 1 }}>✕</span>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#dc2626', marginBottom: 2 }}>
                      {e.title}
                    </div>
                    <div style={{ fontSize: 12, color: '#7f1d1d', lineHeight: 1.5 }}>
                      {e.detail}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Next steps */}
            <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }}>
              <div style={{
                fontSize: 11, fontWeight: 700, letterSpacing: '.06em',
                textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 10
              }}>
                What would you like to do?
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <div style={{ padding: '14px 16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', background: '#fafafa' }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                    Fix my file
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.55, marginBottom: 12 }}>
                    Update the values in your file to match what the schema expects, then re-upload.
                  </div>
                  <Link href="/data/upload" className="btn-primary" style={{ textDecoration: 'none', fontSize: 11, height: 28, display: 'inline-flex', alignItems: 'center', padding: '0 12px' }}>
                    ↑ Upload again
                  </Link>
                </div>
                <div style={{ padding: '14px 16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', background: '#fafafa' }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                    Update the schema
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.55, marginBottom: 12 }}>
                    If your file is correct, delete the existing dataset first, then create a new schema and re-upload. Requires Data Admin permissions.
                  </div>
                  <Link href="/catalog" className="btn-secondary" style={{ textDecoration: 'none', fontSize: 11, height: 28, display: 'inline-flex', alignItems: 'center', padding: '0 12px' }}>
                    Go to Catalog →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Non-failed job with no errors — back link */}
      {!hasFailed && (
        <div style={{ marginTop: 8 }}>
          <Link href="/tasks" style={{ fontSize: 12, color: 'var(--text-tertiary)', textDecoration: 'none' }}>
            ← Back to Jobs
          </Link>
        </div>
      )}
    </div>
  )
}

export default GetJob

GetJob.getLayout = (page: ReactNode) => (
  <AccountLayout title="Job Detail">{page}</AccountLayout>
)
