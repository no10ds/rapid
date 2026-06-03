// Formats an ISO-style date string (or anything Date can parse) as
// "23 Aug 2026 14:05". Falls back to the raw string if unparseable, '—' if absent.
export function formatDate(raw: string | undefined): string {
  if (!raw) return '—'
  const d = new Date(raw)
  if (isNaN(d.getTime())) return raw
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

// Formats a unix timestamp (seconds, number or numeric string) for display.
// Returns null when the input is missing or unparseable.
export function formatTs(
  ts: number | string | undefined,
  style: 'short' | 'long' = 'short'
): string | null {
  if (!ts) return null
  const seconds = typeof ts === 'string' ? parseInt(ts, 10) : ts
  if (!seconds || isNaN(seconds)) return null
  const options: Intl.DateTimeFormatOptions =
    style === 'long'
      ? { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' }
      : { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }
  return new Date(seconds * 1000).toLocaleString('en-GB', options)
}
