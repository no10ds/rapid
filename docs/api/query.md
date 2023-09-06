Data can be queried provided data has been uploaded at some point in the past.

## Construct Query

There are six values you can customise:

- `select_columns`
  - Which column(s) you want to select
  - List of strings
  - Can contain aggregation functions e.g.: `"avg(col1)"`, `"sum(col2)"`
  - Can contain renaming of columns e.g.: `"col1 AS custom_name"`
- `filter`
  - How to filter the data
  - This is provided as a raw SQL string
  - Omit the `WHERE` keyword
- `group_by_columns`
  - Which columns to group by
  - List of column names as strings
- `aggregation_conditions`
  - What conditions you want to apply to aggregated values
  - This is provided as a raw SQL string
  - Omit the `HAVING` keyword
- `order_by_columns`
  - By which column(s) to order the data
  - List of strings
  - Defaults to ascending (`ASC`) if not provided
- `limit`
  - How many rows to limit the results to
  - String of an integer

For example:

```json
{
  "select_columns": ["col1", "avg(col2)"],
  "filter": "col2 >= 10",
  "group_by_columns": ["col1"],
  "aggregation_conditions": "avg(col2) <= 15",
  "order_by_columns": [
    {
      "column": "col1",
      "direction": "DESC"
    },
    {
      "column": "col2",
      "direction": "ASC"
    }
  ],
  "limit": "30"
}
```

> Note: If you do not specify a customised query, and only provide the domain and dataset, you will **select the entire dataset**
