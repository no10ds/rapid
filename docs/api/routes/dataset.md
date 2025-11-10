## Upload

Given a schema has been uploaded you can upload data which matches that schema. Uploading a CSV/Parquet file via this endpoint
ensures that the data matches the schema and that it is consistent and sanitised. Should any errors be detected during
upload, these are sent back in the response to facilitate you fixing the issues.

### Permissions

You will need a relevant `WRITE` permission that matches the dataset sensitivity level, e.g.: `WRITE_ALL`, `WRITE_PUBLIC`, `WRITE_PRIVATE`, `WRITE_PROTECTED_{DOMAIN}`.

### Path

`POST /datasets/{layer}/{domain}/{dataset}`

### Inputs

| Parameters | Required | Usage                                   | Example values              | Definition              |
| ---------- | -------- | --------------------------------------- | --------------------------- | ----------------------- |
| `layer`    | True     | URL parameter                           | `default`                   | layer of the dataset    |
| `domain`   | True     | URL parameter                           | `air`                       | domain of the dataset   |
| `dataset`  | True     | URL parameter                           | `passengers_by_airport`     | dataset title           |
| `version`  | False    | Query parameter                         | `3`                         | dataset version         |
| `file`     | True     | File in form data with key value `file` | `passengers_by_airport.csv` | the dataset file itself |

### Outputs

If successful returns file name with a timestamp included, e.g.:

```json
{
  "details": {
    "original_filename": "the-filename.csv",
    "raw_filename": "661c9467-5d0e-4ec7-ad05-b8651598b675.csv",
    "dataset_version": 3,
    "status": "Data processing",
    "job_id": "3bd7d98f-2264-4f88-bd65-5a2089161650"
  }
}
```

## Delete

Use this endpoint to delete all the contents linked to a layer/domain/dataset. It deletes the table, raw data, uploaded data and all schemas. When all valid items in the domain/dataset have been deleted, a success message will be displayed.

### Permissions

`DATA_ADMIN`

### Path

`DELETE /datasets/{layer}/{domain}/{dataset}`

### Inputs

| Parameters | Required | Usage         | Example values   | Definition            |
| ---------- | -------- | ------------- | ---------------- | --------------------- |
| `layer`    | True     | URL parameter | `raw`            | layer of the dataset  |
| `domain`   | True     | URL parameter | `land`           | domain of the dataset |
| `dataset`  | True     | URL parameter | `train_journeys` | dataset title         |

### Outputs

If successful returns the dataset has been deleted

```json
{
  "details": "{dataset} has been deleted."
}
```

## Delete Data File

Use this endpoint to delete a specific file linked to a `layer/domain/dataset/version`. If there is no data stored for the
`layer/domain/dataset/version` or the file name is invalid an error will be thrown.

When a valid file in the `layer/domain/dataset/version` is deleted, a success message will be displayed.

### Permissions

You will need a relevant `WRITE` permission that matches the dataset sensitivity level, e.g.: `WRITE_ALL`, `WRITE_PUBLIC`, `WRITE_PRIVATE`, `WRITE_PROTECTED_{DOMAIN}`.

### Path

`DELETE /datasets/{layer}/{domain}/{dataset}/{version}/{filename}`

### Inputs

| Parameters | Required | Usage         | Example values                  | Definition                    |
| ---------- | -------- | ------------- | ------------------------------- | ----------------------------- |
| `layer`    | True     | URL parameter | `raw`                           | layer of the dataset          |
| `domain`   | True     | URL parameter | `land`                          | domain of the dataset         |
| `dataset`  | True     | URL parameter | `train_journeys`                | dataset title                 |
| `version`  | True     | URL parameter | `3`                             | dataset version               |
| `filename` | True     | URL parameter | `2022-01-21T17:12:31-file1.csv` | previously uploaded file name |

### Outputs

If successful returns the file has been deleted

```json
{
  "details": "{filename} has been deleted."
}
```

## List

Use this endpoint to retrieve a list of available datasets. You can also filter by the dataset sensitivity level or by
tags specified on the dataset.

If you do not specify any filter values, you will retrieve all available datasets.

You can optionally enrich the information returned, this will include values like `Last Updated Time`, `Description` and `Tags`.

### Required Permissions

None

### Path

`POST /datasets/`

### Inputs

| Parameters | Required | Usage                   | Example values                                                                                 | Definition            |
| ---------- | -------- | ----------------------- | ---------------------------------------------------------------------------------------------- | --------------------- |
| enriched   | False    | Boolean Query parameter | True                                                                                           | enriches the metadata |
| query      | False    | JSON Request Body       | Consult the [docs](https://rapid.readthedocs.io/en/latest/api/routes/dataset/#filtering-query) | the filtering query   |

#### Filtering Query

**Example 1 - Filtering by tags**

Here we retrieve all datasets that have a tag with key `tag1` with any value and `tag2` with value `value2`.

```json
{
  "key_value_tags": {
    "tag1": null,
    "tag2": "value2"
  }
}
```

**Example 2 - Filtering by sensitivity**

```json
{
  "sensitivity": "PUBLIC"
}
```

**Example 3 - Filtering by tags and sensitivity**

```json
{
  "sensitivity": "PUBLIC",
  "key_value_tags": {
    "tag1": null,
    "tag2": "value2"
  }
}
```

**Example 4 - Filtering by key value tags and key only tags**

```json
{
  "sensitivity": "PUBLIC",
  "key_value_tags": {
    "tag2": "value2"
  },
  "key_only_tags": ["tag1"]
}
```

### Outputs

Returns a list of datasets matching the query request, e.g.:

```json
[
  {
    "layer": "layer",
    "domain": "military",
    "dataset": "purchases",
    "version": 1,
    "tags": {
      "tag1": "weaponry",
      "sensitivity": "PUBLIC",
      "no_of_versions": "1"
    }
  },
  {
    "domain": "military",
    "dataset": "armoury",
    "version": 1,
    "tags": {
      "tag1": "weaponry",
      "sensitivity": "PRIVATE",
      "no_of_versions": "1"
    }
  }
]
```

If no dataset exists or none that matches the query, you will get an empty response, e.g.:

```json
[]
```

## List Raw Files

Use this endpoint to retrieve all raw files linked to a specific layer/domain/dataset/version, if there is no data stored for the layer/domain/dataset/version an error will be thrown.

When a valid domain/dataset/version is retrieved the available raw file uploads will be displayed in list format.

### Required Permissions

None

### Path

`GET /datasets/{layer}/{domain}/{dataset}/{version}/files`

### Inputs

| Parameters | Required | Usage         | Example values   | Definition            |
| ---------- | -------- | ------------- | ---------------- | --------------------- |
| `layer`    | True     | URL parameter | `raw`            | layer of the dataset  |
| `domain`   | True     | URL parameter | `land`           | domain of the dataset |
| `dataset`  | True     | URL parameter | `train_journeys` | dataset title         |
| `version`  | True     | URL parameter | `3`              | dataset version       |

### Outputs

List of raw files in json format, e.g.:

```json
["2022-01-21T17:12:31-file1.csv", "2022-01-24T11:43:28-file2.csv"]
```

## Query

Data can be queried provided data has been uploaded at some point in the past. Large datasets are not supported by this endpoint.

### Required Permissions

You will need `READ` permission appropriate to the dataset sensitivity level, e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`.

### Path

`POST /datasets/{layer}/{domain}/{dataset}/query`

### Inputs

| Parameters | Required | Usage             | Example values                                                        | Definition            |
| ---------- | -------- | ----------------- | --------------------------------------------------------------------- | --------------------- |
| `layer`    | True     | URL parameter     | `raw`                                                                 | layer of the dataset  |
| `domain`   | True     | URL parameter     | `space`                                                               | domain of the dataset |
| `dataset`  | True     | URL parameter     | `rocket_launches`                                                     | dataset title         |
| `version`  | False    | Query parameter   | '3'                                                                   | dataset version       |
| `query`    | False    | JSON Request Body | Consult the [docs](https://rapid.readthedocs.io/en/latest/api/query/) | the query object      |

### Outputs

#### JSON

By default, the result of the query are returned in JSON format where each key represents a row, e.g.:

```json
{
    "0": {
        "column1": "value1",
        "column2": "value2"
    },
    ...
}
```

#### CSV

To get a CSV response, the `Accept` Header has to be set to `text/csv`, this can be set below. The response will come as a table, e.g.:

```csv
"","column1","column2"
0,"value1","value2"
...
```

## Query Large

Data can be queried provided data has been uploaded at some point in the past. This endpoint allows querying datasets larger than 100,000 rows.

> The only download format currently available is `CSV`

### Required Permissions

You will need a `READ` permission appropriate to the dataset sensitivity level, e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`.

### Path

`POST /datasets/{layer}/{domain}/{dataset}/query/large`

### Inputs

| Parameters | Required | Usage             | Example values                                                        | Definition            |
| ---------- | -------- | ----------------- | --------------------------------------------------------------------- | --------------------- |
| `layer`    | True     | URL parameter     | `raw`                                                                 | layer of the dataset  |
| `domain`   | True     | URL parameter     | `space`                                                               | domain of the dataset |
| `dataset`  | True     | URL parameter     | `rocket_launches`                                                     | dataset title         |
| `version`  | False    | Query parameter   | '3'                                                                   | dataset version       |
| `query`    | False    | JSON Request Body | Consult the [docs](https://rapid.readthedocs.io/en/latest/api/query/) | the query object      |

### Outputs

Asynchronous Job ID that can be used to track the progress of the query. Once the query has completed successfully, you can query the `/jobs/<job-id>` endpoint to retrieve the download URL for the query results

## Dataset Info

Use this endpoint to retrieve basic information for specific datasets, if there is no data stored for the dataset an error will be thrown.

When a valid dataset is retrieved the available data will be the schema definition with some extra values such as: - number of rows - number of columns - statistics data for date columns

### Required Permissions

You will need any `READ` permission, e.g.: `READ_ALL`, `READ_PUBLIC`, `READ_PRIVATE`, `READ_PROTECTED_{DOMAIN}`.

### Path

`GET /datasets/{layer}/{domain}/{dataset}/info`

### Inputs

| Parameters | Required | Usage           | Example values   | Definition            |
| ---------- | -------- | --------------- | ---------------- | --------------------- |
| `layer`    | True     | URL parameter   | `raw`            | layer of the dataset  |
| `domain`   | True     | URL parameter   | `land`           | domain of the dataset |
| `dataset`  | True     | URL parameter   | `train_journeys` | dataset title         |
| `version`  | False    | Query parameter | `3`              | dataset version       |

### Outputs

Schema in json format in the response body:

```json
{
  "metadata": {
    "layer": "default",
    "domain": "dot",
    "dataset": "trains_departures",
    "sensitivity": "PUBLIC",
    "version": 3,
    "tags": {},
    "owners": [
      {
        "name": "user_name",
        "email": "user@email.email"
      }
    ],
    "update_behaviour": "APPEND",
    "number_of_rows": 123,
    "number_of_columns": 2,
    "last_updated": "2022-03-01 11:03:49+00:00"
  },
  "columns": [
    {
      "name": "date",
      "partition_index": 0,
      "data_type": "date",
      "format": "%d/%m/%Y",
      "allow_null": false,
      "statistics": {
        "max": "2021-07-01",
        "min": "2014-01-01"
      }
    },
    {
      "name": "num_journeys",
      "partition_index": null,
      "data_type": "integer",
      "allow_null": false,
      "statistics": null
    }
  ]
}
```
