# Changelog

All notable changes to this project will be documented in this file. This project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v6.2.1 - _2023-05-10_

See [v6.2.1] changes

### Fixed

- An error with the delete dataset endpoint

## v6.2.0 - _2023-05-10_

See [v6.2.0] changes

### Added

- The list datasets endpoint now provides the Last Updated Datetime for each dataset

## v6.1.0 - _2023-05-03_

See [v6.1.0] changes

### Added

- rAPId can now handle schemas being generated and data being uploaded in Apache Parquet Format.

### Changed

- When uploading a file into rAPId we automatically reject any file now that does not match a csv or Apache Parquet format. Before we used to handle the file regardless and wait for a exception being raised from within the api.

### Fixed

- When calling the list all datasets endpoint we now filter this list based on the permissions that the user has access to.


[v6.1.0]: https://github.com/no10ds/rapid-api/compare/v6.0.2...v6.1.0

## v6.0.2 - _2023-03-24_

See [v6.0.2] changes

### Fixed

- Fixed a bug concerning dataset uploading with overwrite behaviour, making it much less brittle.

[v6.0.2]: https://github.com/no10ds/rapid-api/compare/v6.0.0...v6.0.2

## v6.0.0 - _2023-03-17_

See [v6.0.0] changes

### Fixed

- All required calls in the API are now paginated by Boto3. This fixes some large issues where, when there were more than 50 crawlers in the account the API would fail to retrieve all datasets as the backend call would paginate onto a next page.
- Fixes an issue where the delete data file endpoint was deleting the raw data file from S3 and now instead deletes the processed file instead.
- Fixes an issue where the uploaded files were temporarily stored with just the name they were uploaded with, this was causing errors if two identically names files were uploaded within a small window.

### Added

- New optional environment variable `CATALOG_DISABLED` that can be passed to disable the internal data catalog if required.
- New endpoint that allows for protected domains to be deleted. Can be called using the method `DELETE /api/protected_domains/{domain}`.
- New endpoint that allows for the entire deletion of a dataset from within rAPId. This new method removes all raw and uploaded data files, any schemas, tables and crawlers. Can be thought of an entire dataset wiping from rAPId. The method can be called using `DELETE /api/datasets/{domain}/{dataset}`.

### Changed

- __Breaking Change__ - Domains are now case insensitive. This fixes an issue where if you created a Protected domain with an uppercase domain and then the same with a lowercase domain the permissions do not match up as they are interpreted as different endpoints. All domains now have to be lower case. To migrate them, you will need to run: `migrations/scripts/v6_domain_case_insensitive.py`.
- When downloading data the extra Pandas DataFrame index column is not included now.
- FastAPI has been upgraded to 0.92.0.

### Migration

To migrate from v5 to v6, you will need to run the migration script: `migrations/scripts/v6_domain_case_insensitive.py`.

This can be done by first installing the Python requirements from `requirements.txt` and then running `python migrations/scripts/v6_domain_case_insensitive.py`

You will also need to provide values for the following environment variables, either by defining them in a `.env` file in the repo root or exporting them to the environment where the script is run.

```
AWS_REGION
DATA_BUCKET
RESOURCE_NAME_PREFIX
AWS_ACCOUNT_ID
```

[v6.0.0]: https://github.com/no10ds/rapid-api/compare/v5.0.2...v6.0.0

## v5.0.2 - _2023-03-09_

See [v5.0.2] changes

### Fixed
- Fetching datasets for the UI was only returning write access

[v5.0.2]: https://github.com/no10ds/rapid-api/compare/v5.0.1...v5.0.2

## v5.0.1 - _2023-02-02_

See [v5.0.1] changes

### Fixed
- Fix data always being written to version 1 location

### Security
- Upgrade GitPython to 3.1.30

[v5.0.1]: https://github.com/no10ds/rapid-api/compare/v5.0.0...v5.0.1


## v5.0.0 - _2022-01-27_

See [v5.0.0] changes

v5.0.0 is a major release of rAPId with several breaking changes. One of the major changes is the splitting out of the user interface into it's own codebase. It also introduces a data catalog metadata search.

### Added

- New description field for dataset schemas. This is a human readable tag that can be applied to datasets so a user can understand the datasets functionaility.
- Dataset metadata search endpoint `/api/datasets/search/{search term}`

### Changed
- Test users are created automatically within the infrastructure now and are prefixed accordingly
- ***(Breaking Change)*** All api routes are now served on the prefix `/api`. For instance the api route to list datasets `GET /datasets` now becomes `GET /api/datasets`
- ***(Breaking Change)*** The storage of the pretty printed JSON schemas has been removed to allow for them be queriable within Athena. This is requied for the data catalog search. To migrate over it is required to run the migration `migrations/scripts/v5_schema_migration.py`.
- Test users are now prefixed as they are generated within the infrastructure.

### Removed

- The simple static user interface hosted within the API has been removed and is now hosted as it's own (service)[https://github.com/no10ds/rapid-ui]


[v5.0.0]: https://github.com/no10ds/rapid-api/compare/v4.2.0...v5.0.0

## v4.2.0 - _2022-12-14_

See [v4.2.0] changes

v4.2.0 Improves the behaviour of the query dataset endpoint to allow the querying of large datasets (>100000 rows)

### Changed

The query dataset endpoint can now be used for the querying of large datasets (>100000 rows), if the query includes a `limit` clause ensuring that less that 100000 rows of data will be returned.

[v4.2.0]: https://github.com/no10ds/rapid-api/compare/v4.1.2...v4.2.0

## v4.1.2 - _2022-11-29_

v4.1.2 Fix for query large dataset client usage

### Fixes
- Fix query large dataset client usage

## v4.1.1 - _2022-11-23_

v4.1.1 fixes a few issues with the schema creation UI

### Fixes
- Create client error
- Organisation typo
- Keep sensitivity on second create schema UI page
- Fix owner name validation for create schema

## v4.1.0 - _2022-11-20_

v4.1.0 introduces a new UI for the easy creation of schemas and the ability to expose the rAPId instance to the Gov UK CDDO Federated API Discovery Model (https://github.com/co-cddo/federated-api-model). Instead of having to use the rAPId endpoints to generate and then upload the schema, the new UI opens a simple flow from uploading a file, to altering the generated schema and to then uploading.

### Added
- UI
  - Schema creation flow
- CDDO Federated API Discovery

## v4.0.0 - _2022-09-21_

See [v4.0.0] changes

v4.0.0 introduces schema versioning for datasets and allows both uploads and downloads. Also, it allows large file
uploads and downloads

### Added
- Schema versioning
  - Schema update endpoint
  - Upload and downloading specific version and latest version by default
- Large file upload/download
  - Track upload/download job status
  - List job status endpoint
- UI
  - Task status flow

### Changed
- Schema versioning
  - New schema upload defaulting to version 1
  - Upload/Download data defaults to latest version

### Security
- Security headers
- Tracing requests by subject ID

[Unreleased changes]: https://github.com/no10ds/rapid-api/compare/v4.0.0...HEAD
[v4.0.0]: https://github.com/no10ds/rapid-api/compare/v3.0.0...v4.0.0

## v3.0.0 - _2022-08-26_

See [v3.0.0] changes

v3.0.0 Provides download functionality in the UI, allowing the user to query. Also, it introduces parquet as the format
to store files, allowing then null values in the datasets.

### Fixed
- Error when querying files with null values on numeric columns.
- Add protected domains to list all datasets endpoint.

### Added
- UI
  - Input validation on subject creation
  - Data management download flow
    - Allow user to download datasets from the UI
    - Allow user to introduce queries

### Changed
- Store files in parquet instead of csv
- Data management migrated to parquet

[v3.0.0]: https://github.com/no10ds/rapid-api/compare/v2.0.0...v3.0.0

## v2.0.0 - _2022-08-19_

See [v2.0.0] changes

v2.0.0 provides a complete overhaul on how we handle authorisation as well as an extended UI.

### Fixed
- Consistent exception handling

### Added
- Endpoints:
  - Create subject
  - List subjects
  - Delete subject
  - Modify subject permissions
  - Get subject permissions
  - Get all permissions
- UI
  - User management flows
  - Data management flows
- UI user journey test

### Changed
- Complete overhaul of authorisation process

[v2.0.0]: https://github.com/no10ds/rapid-api/compare/v1.3.0...v2.0.0

## v1.3.0 - _2022-06-17_

See [v1.3.0] changes

### Added
- Getting started documentation to walkthrough dataset uploading and querying

### Fixed
- Add `resource_prefix` to the necessary AWS resources to enable the hosting of multiple rAPId instances

[v1.3.0]: https://github.com/no10ds/rapid-api/compare/v1.2.0...v1.3.0

## v1.2.0 - _2022-05-31_

See [v1.2.0] changes

### Added
- Documentation improvements
  - OpenAPI spec includes endpoint behaviour documentation
  - Added example scripts for programmatic interaction

[v1.2.0]: https://github.com/no10ds/rapid-api/compare/v1.1.0...v1.2.0

## v1.1.0 - _2022-05-29_

See [v1.1.0] changes

### Added
- Protected domains:
  - Allows the separation of access permissions for specific `protected domains`
  - See the data acccess [docs](./docs/guides/usage/data_access.md)
  - See usage [docs](./docs/guides/usage/usage.md#domain)
- Overwrite update behaviour:
  - Allows datasets to be overwritten when a new file is uploaded, rather than just appended to
  - See the schema creation [docs](./docs/guides/usage/schema_creation.md#update-behaviour)

[v1.1.0]: https://github.com/no10ds/rapid-api/compare/v1.0.0...v1.1.0


## v1.0.0 - _2022-05-10_

See [v1.0.0] changes

### Added
- Documentation and usage guides can be found [here](https://github.com/no10ds/rapid-api/tree/master/docs)
- First full application release
- Features:
  - Generate a schema from a dataset
  - Upload a schema
  - Upload a dataset
  - List available datasets
  - Get metadata information for a dataset
  - Query a previously uploaded dataset
  - Add a new client app

[Unreleased changes]: https://github.com/no10ds/rapid-api/compare/v1.0.0...HEAD
[v1.0.0]: https://github.com/no10ds/rapid-api/compare/ff60bf65...v1.0.0
