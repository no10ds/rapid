The rAPId API serves to make data storage and retrieval consistent for all users involved.

Overarching API functionality includes:

- [Uploading a schema (i.e.: creating a new dataset definition)](/api/routes/schema/)
    - Also creating a new version of an existing schema
- [Uploading data to any version of a dataset](/api/routes/dataset/#upload)
- [Listing available data](/api/routes/dataset/#list)
- [Querying data from any version of a dataset](/api/routes/dataset/#query)
- [Deleting data](/api/routes/dataset/#delete-data-file)
- Creating [users](/api/routes/user/#create) and [clients](/api/routes/client/#create)
- [Managing user and client permissions](/api/routes/subject/#modify-subject-permissions)

## Application Usage Overview

The first step is to create a dataset by uploading a schema that describes the metadata including e.g.: data owner, tags, partition columns, data types, auto-generated version, etc..

Then the data can be uploaded to the dataset. During the upload process, the service checks if the data matches the previously uploaded dataset schema definition and transforms it into `.parquet`. The data can then be queried.

The application can be used by both human and programmatic clients (see more below)

- When accessing the REST API as a client application, different actions require the client to have different
  permissions e.g.:`READ`, `WRITE`, `DATA_ADMIN`, etc., and different dataset sensitivity level permissions
  e.g.: `PUBLIC`, `PRIVATE`, etc.
- When accessing the UI as a human user, permissions are granted by the permissions' database, e.g.: `WRITE_PUBLIC`

## Data upload and query flows

### No schema exists + upload data + query

![general usage flow image](../diagrams/general_usage_flow.png)

### Schema exists + upload data + query

![upload and query image](../diagrams/upload_and_query_data.png)

### Schema exists + upload large dataset + query

![upload and query image](../diagrams/upload_and_query_large_data.png)
