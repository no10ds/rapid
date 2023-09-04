## Generate

In order to upload the dataset for the first time, you need to define its schema. This endpoint is provided for your convenience to generate a schema based on an existing dataset.

> The first 50MB of the uploaded file (regardless of size) are used to infer the schema. Consider uploading a representative sample of your dataset (e.g.: the first 10,000 rows) instead of uploading the entire large file which could take a long time

### Permissions

Any

### Path

`POST /schema/{sensitivity}/{domain}/{dataset}/generate`

### Inputs

| Parameters    | Usage                                   | Example values               | Definition                 |
| ------------- | --------------------------------------- | ---------------------------- | -------------------------- |
| `layer`       | URL parameter                           | `default`                    | layer of the dataset       |
| `sensitivity` | URL parameter                           | `PUBLIC, PRIVATE, PROTECTED` | sensitivity of the dataset |
| `domain`      | URL parameter                           | `land`                       | domain of the dataset      |
| `dataset`     | URL parameter                           | `train_journeys`             | dataset title              |
| `file`        | File in form data with key value `file` | `train_journeys.csv`         | the dataset file itself    |

### Outputs

Schema in json format in the response body:

```json
{
  "metadata": {
    "layer": "default",
    "domain": "land",
    "dataset": "train_journeys",
    "sensitivity": "PUBLIC",
    "key_value_tags": {},
    "key_only_tags": [],
    "owners": [
      {
        "name": "change_me",
        "email": "change_me@email.com"
      }
    ],
    "update_behaviour": "APPEND"
  },
  "columns": [
    {
      "name": "date",
      "partition_index": 0,
      "data_type": "date",
      "format": "%d/%m/%Y",
      "allow_null": false
    },
    {
      "name": "num_journeys",
      "partition_index": null,
      "data_type": "integer",
      "allow_null": false
    }
  ]
}
```

## Upload

When you have a schema definition you can use this endpoint to upload it. This will allow you to subsequently upload datasets that match the schema.

### Permissions

`DATA_ADMIN`

### Path

`POST /schema`

### Inputs

| Parameters | Usage             | Example values | Definition            |
| ---------- | ----------------- | -------------- | --------------------- |
| schema     | JSON request body | see below      | the schema definition |

Example schema JSON body:

```json
{
  "metadata": {
    "layer": "default",
    "domain": "land",
    "dataset": "train_journeys",
    "sensitivity": "PUBLIC",
    "key_value_tags": {
      "train": "passenger"
    },
    "key_only_tags": ["land"],
    "owners": [
      {
        "name": "Stanley Shunpike",
        "email": "stan.shunpike@email.com"
      }
    ],
    "update_behaviour": "APPEND"
  },
  "columns": [
    {
      "name": "date",
      "partition_index": 0,
      "data_type": "date",
      "format": "%d/%m/%Y",
      "allow_null": false
    },
    {
      "name": "num_journeys",
      "partition_index": null,
      "data_type": "integer",
      "allow_null": false
    }
  ]
}
```

### Outputs

None

## Update (new dataset version)

This endpoint is for uploading an updated schema definition. This will allow you to subsequently upload datasets that match the updated schema.

### Permissions

Any relevant `WRITE` permissions that matches dataset sensitivity level, e.g. `WRITE_ALL`, `WRITE_PUBLIC`, `WRITE_PRIVATE`, `WRITE_PROTECTED_{DOMAIN}`.

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

### Output

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
