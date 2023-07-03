# Changelog

## v6.2.0 - _2023-03-21_

See [v6.2.0] changes

### Changed

- The upload data page now tracks the upload progress

## v6.0.1 - _2023-03-21_

See [v6.0.1] changes

### Fixed

- The delete data option is now only displayed to users with the DATA_ADMIN permission.

## v6.0.0 - _2023-03-17_

See [v6.0.0] changes

### Added
- New UI endpoint for deleting an entire dataset.

### Changed
- When the API does not include the internal data catalog we do not show the catalog option on the sidebar.
- When downloading data with multiple versions we now default to the most recent version instead of the first version.
- When uploading data we change the upload complete alert from a success to an info. This nudges the user more to release that the data is still processing.

### Fixed
- Handles case when no data is present within rAPId. Before the UI would crash.

## v5.0.2 - _2023-03-09_

See [v5.0.2] changes

### Fixed

- Fetch available datasets separately for both Read and Write access

## v5.0.1 - _2023-01-02_

See [v5.0.1] changes

### Fixed

- Removed the need to have API_URL environment variable. Fixes issue with this sometimes being undefined.

## v5.0.0 - _2023-01-24_

See [v5.0.0] changes

### Added 
- Initial release of new rAPId UI

[v6.2.0]: https://github.com/no10ds/rapid-ui/compare/v6.0.1...v6.2.0
[v6.0.1]: https://github.com/no10ds/rapid-ui/compare/v6.0.0...v6.0.1
[v6.0.0]: https://github.com/no10ds/rapid-ui/compare/v5.0.2...v6.0.0
[v5.0.2]: https://github.com/no10ds/rapid-ui/comapre/v5.0.1...v5.0.2
[v5.0.1]: https://github.com/no10ds/rapid-ui/compare/v5.0.0...v5.0.1
[v5.0.0]: https://github.com/no10ds/rapid-ui/compare/<previous_version>...v5.0.0