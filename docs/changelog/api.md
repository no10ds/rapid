# API Changelog

## v7.12.0 - _2025-05-19_

- Enhancement of E2E tests in rAPId. Should cover most endpoints now.
- Enable SQL injection protection to be turned off conditionally in the WAF
- Allow rAPId to set columns to have unique values

### Fixes:

- Fix issue with empty string columns in rAPId

## v7.11.3 - _2025-03-26_

### Fixes

- Remove `Content-Type: 'application/json'` header from file upload calls to the API.

## v7.11.2 - _2025-03-11_

### Fixes

- FastAPI update requires content-type header for API calls

## v7.11.1 - _2025-03-11_

### Fixes

- Fix release issues

## v7.11.0 - _2024-09-26_

### Fixes

- Removed dependency on batect
- Removed the need to copy the access token when running the UI locally
- Refactored the e2e tests

## v7.10.0 - _2024-03-21_

### Fixes

- Issues with the documentation where links were not re-directing successfully.

### Features

- Extra infrastructure output blocks

## v7.0.9 - _2024-02-06_

### Features

- Ability to pass a custom regex for username validation. See the documentation on the [`custom_user_name_regex`](https://rapid.readthedocs.io/en/latest/infrastructure/deployment/#usage) variable.
- Decoupled API & SDK into separate releases.
- New optional infrastructure variables to increase cpu and memory limits for the API container. See the [infrastructure variables for more information](https://rapid.readthedocs.io/en/latest/infrastructure/deployment/#usage).
- Upgraded `browserify-sign` from 4.2.1 to 4.2.2.
- Upgraded `@adobe/css-tools` from 4.3.1 to 4.3.2.

### Fixes

- Issue with the last updated date on datasets being 'Never Updated'.

### Breaking Changes

### Migration

## v7.0.8 - _2023-11-15_

### Fixes

- Issue with date types when editing a schema on the UI because of no option to apply format column and therefore getting an _all fields are required_ error.
- Tweaked UI design when adding permissions to subject.
- Updated NextJS and Zod package version.

### Features

- Data bucket now has EventBridge notifications enabled by default.

### Closes relevant GitHub issues

- https://github.com/no10ds/rapid/issues/57

## v7.0.7 - _2023-11-07_

### Fixes

- Hitting maximum security group rules for the load balancer.
- Documentation improvements and removes any references to the old deprecated repositories.

### Closes relevant GitHub issues

- https://github.com/no10ds/rapid/issues/50
- https://github.com/no10ds/rapid/issues/59
- https://github.com/no10ds/rapid/issues/54
- https://github.com/no10ds/rapid/issues/51

## v7.0.6 - _2023-10-18_

### Features

- New UI page that allows for the ability to delete users and clients easily.
- Clients can now be created and deleted via the sdk.

### Fixes

- Where dataset info was being called on columns with a date type, this was causing an issue with the Pydantic validation.
- Tweaked the documentation to implement searching for column heading style guide to match what the API returns in the error message.

## v7.0.4 - _2023-09-20_

### Features

- Improved release process
- Added Athena workgroup and database as outputs of the rAPId module.

### Fixes

- Updated terraform default `application_version` and `ui_version` variables.
- Migration script and documentation.

## v7.0.3 - _2023-09-15_

### Fixes

- Fixes issue where permissions were not being correctly read and causing api functionality to fail

## v7.0.2 - _2023-09-14_

### Fixes

- Update UI repo references.

## v7.0.1 - _2023-09-13_

### Fixes

- Date types were being stored as strings which caused issues when querying with Athena. They are now stored as date types.

## v7.0.0 - _2023-09-12_

### Features

- Layers have been introduced to rAPId. These are now the highest level of grouping for your data. They allow you to separate your data into areas that relate to the layers in your data architecture e.g `raw`, `curated`, `presentation`. You will need to specify your layers when you create or migrate a rAPId instance.
- All the code is now in this monorepo. The previous [Infrastructure](https://github.com/no10ds/rapid-infrastructure), [UI](https://github.com/no10ds/rapid-ui) and [API](https://github.com/no10ds/rapid-api) repos are now deprecated. This will ease the use and development of rAPId.
- Schemas are now stored in DynamoDB, rather than S3. This offers speed and usability improvements, as well as making rAPId easier to extend.
- Code efficiency improvements. There were several areas in rAPId where we were executing costly operations that caused performance to degrade at scale. We've fixed these inefficiencies, taking us from O(n²) -> O(n) in these areas.
- Glue Crawlers have been removed, with Athena tables are created directly by the API instead. Data is now available to query immediately after it is uploaded, rather than the previous wait (approximately 3 mins) while crawlers ran. It also offers scalability benefits because without crawlers we are not dependant on the number of free IPs within the subnet.
- Improved UI testing with Playwright.

### Breaking Changes

- All dataset endpoints will be prefixed with `layer`. Typically going from `domain/dataset` to `layer/domain/dataset`.

### Migration

- See the [migration doc](migration.md) for details on how to migrate to v7 from v6.
