# Changelog

## v7.0.0 / v0.1.0 (sdk) - _2023-09-12_

See [v7.0.0 / v0.1.0 (sdk)] changes.

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

[Unreleased changes]: https://github.com/no10ds/rapid/compare/v7.0.0...HEAD
[v7.0.0 / v0.1.0 (sdk)]: https://github.com/no10ds/rapid/v7.0.0
