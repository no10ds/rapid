# SDK Changelog

## v0.1.7 - _2023-02-06_

### Features

- Ability to now create a protected domain via the sdk.

## v0.1.6 - _2023-11-15_

### Fixes

- SDK not uploading a Pandas Dataframe with a date field set correctly.

### Closes relevant GitHub issues

- https://github.com/no10ds/rapid/issues/57

## v0.1.5 - _2023-11-07_

### Fixes

- Issue within the sdk `upload_and_create_dataset` function where schema metadata wasn't being correctly overridden.
- Documentation improvements and removes any references to the old deprecated repositories.

## v0.1.4 - _2023-10-18_

### Features

- Clients can now be created and deleted via the sdk.

### Fixes

- Fixed an issue with the sdk not showing schemas were created successfully due to a wrong response code.
- Where dataset info was being called on columns with a date type, this was causing an issue with the Pydantic validation.
- Tweaked the documentation to implement searching for column heading style guide to match what the API returns in the error message.

## v0.1.3 - _2023-09-20_

### Fixes

- Fix the behaviour of the dataset pattern functions in the SDK.

## v0.1.2 - _2023-09-13_

### Fixes

- Date types were being stored as strings which caused issues when querying with Athena. They are now stored as date types.
- Rename the rAPId sdk method `generate_info` to `fetch_dataset_info` and remove an unnecessary argument.

## v0.1.1- _2023-09-12_

### Features

- Layers have been introduced to rAPId. These are now the highest level of grouping for your data. They allow you to separate your data into areas that relate to the layers in your data architecture e.g `raw`, `curated`, `presentation`. You will need to specify your layers when you create or migrate a rAPId instance.
- All the code is now in this monorepo. The previous [Infrastructure](https://github.com/no10ds/rapid-infrastructure), [UI](https://github.com/no10ds/rapid-ui) and [API](https://github.com/no10ds/rapid-api) repos are now deprecated. This will ease the use and development of rAPId.
- Schemas are now stored in DynamoDB, rather than S3. This offers speed and usability improvements, as well as making rAPId easier to extend.
- Code efficiency improvements. There were several areas in rAPId where we were executing costly operations that caused performance to degrade at scale. We've fixed these inefficiencies, taking us from O(n²) -> O(n) in these areas.
- Glue Crawlers have been removed, with Athena tables are created directly by the API instead. Data is now available to query immediately after it is uploaded, rather than the previous wait (approximately 3 mins) while crawlers ran. It also offers scalability benefits because without crawlers we are not dependant on the number of free IPs within the subnet.
- Improved UI testing with Playwright.

### Breaking Changes

- All dataset endpoints will be prefixed with `layer`. Typically going from `domain/dataset` to `layer/domain/dataset`.
- All sdk functions that interact with datasets will now require an argument for layer.

### Migration

- See the [migration doc](migration.md) for details on how to migrate to v7 from v6.

[Unreleased changes]: https://github.com/no10ds/rapid/compare/v7.0.8...HEAD
[v7.0.8 / v0.1.6 (sdk)]: https://github.com/no10ds/rapid/v7.0.7...v7.0.8
[v7.0.7 / v0.1.5 (sdk)]: https://github.com/no10ds/rapid/v7.0.6...v7.0.7
[v7.0.6 / v0.1.4 (sdk)]: https://github.com/no10ds/rapid/v7.0.5...v7.0.6
[v7.0.5 / v0.1.3 (sdk)]: https://github.com/no10ds/rapid/v7.0.4...v7.0.5
[v7.0.4 / v0.1.2 (sdk)]: https://github.com/no10ds/rapid/v7.0.3...v7.0.4
[v7.0.3 / v0.1.2 (sdk)]: https://github.com/no10ds/rapid/v7.0.2...v7.0.3
[v7.0.2 / v0.1.2 (sdk)]: https://github.com/no10ds/rapid/v7.0.1...v7.0.2
[v7.0.1 / v0.1.2 (sdk)]: https://github.com/no10ds/rapid/v7.0.0...v7.0.1
[v7.0.0 / v0.1.1 (sdk)]: https://github.com/no10ds/rapid/v7.0.0
