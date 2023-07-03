# 0008 - Implement Schema Versioning

Date: 2022-08-28

## Status

Accepted

## People Involved

Lewis Card, Claude Paret, Cristhian Da Silva, Lydia Adejumo, Shashin Dayanand, Jowita Podolak

## Context

We want to enable users to update the version of the datasets so that they can add/remove columns, metadata, among other
information. At the moment the application does not handle these types of changes and a new dataset has to be created
for each version, therefore, a new crawler will be created per dataset making the rAPId instance to reach the limit of
crawlers quickly.

We have discussed possible ways to use 1 crawler for different versions and allow the users to easily update their
datasets definitions.

## Decision
1. Create V1 for a new dataset in the create schema endpoint.
2. Fail the request in create schema if the dataset already exist.
3. Implement a update schema endpoint.
4. Automatically increment the version of the dataset.
5. Update the S3 structure to work with versioning.
6. Update the crawler config to create tables based on versions of any given dataset.
7. Update the crawler with `no_of_versions` tag.
8. Migration scripts to move from the old format to the new.

## Consequences
1. Major changes in the code and structure leading to breaking changes for the application.
2. Crawlers performance will be impacted for big datasets when adding more versions.
3. Users with older version (before release v3.0.0) will have to migrate to a new structure (we created [script](test/scripts/migrate_datasets_to_new_versioning_structure.py) to support this)
