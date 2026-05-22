export type QueryBodyInput = {
  select_columns: string
  filter: string
  group_by_columns: string
  aggregation_conditions: string
  limit: string
}

// Builds the API payload from form state, dropping empty fields and
// splitting comma-separated lists into arrays.
export function buildQueryPayload(queryBody: QueryBodyInput): Record<string, unknown> {
  const payload: Record<string, unknown> = {}
  if (queryBody.select_columns) payload.select_columns = queryBody.select_columns.split(',')
  if (queryBody.filter) payload.filter = queryBody.filter
  if (queryBody.group_by_columns) payload.group_by_columns = queryBody.group_by_columns.split(',')
  if (queryBody.aggregation_conditions) payload.aggregation_conditions = queryBody.aggregation_conditions
  if (queryBody.limit) payload.limit = queryBody.limit
  return payload
}
