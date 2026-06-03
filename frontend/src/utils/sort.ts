// Returns a stable copy of `items` sorted by the string value at `key`.
// Pass null/undefined for `key` to skip sorting and return `items` unchanged.
// Comparison is case- and accent-insensitive.
export function sortByString<T>(
  items: T[],
  key: keyof T | null | undefined,
  direction: 'asc' | 'desc'
): T[] {
  if (!key) return items
  const sign = direction === 'asc' ? 1 : -1
  return [...items].sort((a, b) =>
    String(a[key] ?? '').localeCompare(String(b[key] ?? ''), undefined, {
      sensitivity: 'base'
    }) * sign
  )
}
