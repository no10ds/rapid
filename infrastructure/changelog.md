# Changelog

All notable changes to this project will be documented in this file. This project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v6.2.1 - _2023-06-29_

See [v6.2.1] changes

### Fixed

- Update UI bucket ownership controls to set ACL. Due to AWS change.


## v6.2.0 - _2023-05-10_

See [v6.2.0] changes

### Fixed

- Password policy rules can now be passed through to all modules in the iam-config block.

## v6.1.0 - _2023-05-03_

See [v6.1.0] changes

### Fixed

- We now apply a WAF oversize handling rule directly through the infrastructure as per https://github.com/hashicorp/terraform-provider-aws/issues/25545.
- When deploying multiple instances of rAPId on a same account but to different environments e.g. dev or prod, some of the infrastructure had conflicting names and therefore would fail to deploy.
- Limit access policy further for the access logs iam policy to pass Checkov scanning.


## v6.0.3 - _2023-04-12_

See [v6.0.3] changes

### Fixed
- Add Glue:GetDatabases permission to ECS task role.
- Make the UI rebuild trigger if the S3 bucket changes.

## v6.0.2 - _2023-03-28_

See [v6.0.2] changes

### Changed
- Limit the size of the random string added to the S3 bucket, due to the 63 character bucket name limit.

## v6.0.1 - _2023-03-21_

See [v6.0.1] changes

### Changed
- Updated the default values for ui_version and application_version to v6.0.1

## v6.0.0 - _2023-03-17_

See [v6.0.0] changes

### Changed
- All terraform providers have been updated and are now consistent across the infrastructure.

### Added
- New variable to be passed into the `app-cluster` if you want to disable the internal API data catalog. Defaults to false but can be set as true.

## v5.0.2 - _2023-03-07_
See [v5.0.2] changes

### Fixed
- Stop cerfiticate validation record duplication

## v5.0.1 - _2023-02-01_
See [v5.0.1] changes

### Fixed
- Removed the requirement to inject a API into the URL

## v5.0.0 - _2023-02-01_
See [v5.0.0] changes

### Added
- Infrastructure required to deploy new UI. It introduces two new variables. `ui_version=v5.0.0` the version of the static UI to download and `us_east_certificate_validation_arn` a new arn required to be created in `us-east-1` for Cloudfront. The following get's created
  - New S3 bucket to host static html files
  - Cloudfront hosting the API in ECS and the S3 static html files
  - Lambda edge function required for the html page routing
- Test clients are now created directly within the infrastructure

### Fixed
- Prevents ECS load balancer from getting deleted
- Removed inline policies in use
- Glue is allowed the PassRole access to allow for schema uploading
- S3 buckets now have SSL restrictions

## v4.2.0 - _2022-12-22_
See [v4.2.0] changes

### Added
- Configurable cognito password policy
- Cloudtrail creation is now optional and cloudtrail events are now consolidated into one trail

## v4.1.1 - _2022-11-23_
See [v4.1.1] changes

### Fixes
- Typo in organisation

## v4.1.0 - _2022-11-20_
See [v4.1.0] changes

### Added
- Read in optional project details for CDDo federated API model
- New global secondary index column for jobs DynamoDB table

## v4.0.0 - _2022-09-21_
See [v4.0.0] changes

### Fixed
- Query results expiry time

### Added
- DynamoDB resource for job status management

## v3.0.0 - _2022-08-26_

See [v3.0.0] changes

### Fixed
- Oversized requests handling

### Added
- Lifecycle policy to ECR

### Changed
- Allow service task to delete parquet files

### Removed
- Custom csv classifier

## v2.0.0 - _2022-08-19_

See [v2.0.0] changes

### Added
- DynamoDB resources for new authorisation structure

### Removed
- Custom permission scopes

### Security
- Handle oversized requests in WAF manually until terraform is updated

## v1.3.0 - _2022-07-25_

See [v1.3.0] changes

### Added
- Documentation and usage guides can be found [here](https://github.com/no10ds/rapid-infrastructure/tree/master/docs)
- First full application release
- Features:
  - Build rapid infrastructure
  - Add release mechanism see [release](https://github.com/no10ds/rapid-infrastructure/blob/main/docs/guides/contributing.md#releasing)

## v1.0.0 - _2022-07-20_

See [v1.0.0] changes

### Added
- Documentation and usage guides can be found [here](https://github.com/no10ds/rapid-infrastructure/tree/master/docs)
- First full application release
- Features:
  - Build rapid infrastructure


[v6.1.0]: https://github.com/no10ds/rapid-infrastructure/compare/v6.0.3...HEAD
[v6.0.3]: https://github.com/no10ds/rapid-infrastructure/compare/v6.0.2...v6.0.3
[v6.0.2]: https://github.com/no10ds/rapid-infrastructure/compare/v6.0.1...v6.0.2
[v6.0.1]: https://github.com/no10ds/rapid-infrastructure/compare/v6.0.0...v6.0.1
[v6.0.0]: https://github.com/no10ds/rapid-infrastructure/compare/v5.0.2...v6.0.0
[v5.0.2]: https://github.com/no10ds/rapid-infrastructure/compare/v5.0.1...v5.0.2
[v5.0.1]: https://github.com/no10ds/rapid-infrastructure/compare/v5.0.0...v5.0.1
[v5.0.0]: https://github.com/no10ds/rapid-infrastructure/compare/v4.2.0...v5.0.0
[v4.2.0]: https://github.com/no10ds/rapid-infrastructure/compare/v4.1.0...v4.2.0
[v4.1.1]: https://github.com/no10ds/rapid-infrastructure/compare/v4.1.0...v4.1.1
[v4.1.0]: https://github.com/no10ds/rapid-infrastructure/compare/v4.0.0...v4.1.0
[v4.0.0]: https://github.com/no10ds/rapid-infrastructure/compare/v3.0.0...v4.0.0
[v3.0.0]: https://github.com/no10ds/rapid-infrastructure/compare/v2.0.0...v3.0.0
[v2.0.0]: https://github.com/no10ds/rapid-infrastructure/compare/v1.3.0...v2.0.0
[v1.3.0]: https://github.com/no10ds/rapid-infrastructure/compare/v1.0.0...v1.3.0
[v1.0.0]: https://github.com/no10ds/rapid-infrastructure/compare/5298389...v1.0.0
