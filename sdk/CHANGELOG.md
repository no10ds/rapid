# Changelog

All notable changes to this project will be documented in this file. This project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.0.8 - _2023-03-07_

See [v0.0.8] changes

### Changed
- Introduced new Pydantic class types for all `rapid.items`. This allows for type validation on the class creation and matches the types within the rAPId to help minimize errors.
- `rapid.Rapid.generate_schema()` now returns the new Pydantic `rapid.items.Schema` class.
- `rapid.Rapid.patterns` now includes common patterns that might be used for data manipulation tasks exploiting the sdk functions for easier use.
- Improved documentation across the entire sdk.

### Removed
- `create` and `update` methods are removed from the old `rapid.items.Schema` class as it didn't make sense to have api calls within classes.

### Added
- New `create_schema` and `update_schema` methods added to the `rapid.Rapid` class. This is to mock the behaviour mentioned above.
- New `rapid.items.Query` Pydantic class that allows for a programmatic definition of a rAPId dataset download.
- New `rapid.Rapid.download_dataset` function. Returns the downloaded Pandas dataframe. This function makes use of the above `Query` class.
- Improved unit testing coverage.

[v0.0.8]: https://github.com/no10ds/rapid-api/compare/720ecd1fd6ce14fc37a3202133ce239419d48f1f...v0.0.8
