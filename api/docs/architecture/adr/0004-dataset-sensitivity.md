# 0004 - Dataset Sensitivity
Date: 2022-02-10

## Status
Accepted

## Context

Datasets have an associated sensitivity level. Current values are one of `PUBLIC`, `PRIVATE` or `PROTECTED`.

We needed a mechanism for tying the sensitivity level to the dataset.

## Decision

We decided to add the sensitivity in several places:

### As part of the schema object S3 path
e.g.: `data/schemas/PUBLIC/{domain}-{dataset}.json`

This allows us to quickly list all the schemas in the directory and parse out the sensitivity without needing to
read each individual schema file to retrieve it, or to query each object separately for its tags.

An example where this is used is in the authorisation flow to determine if the user has permission to view this dataset.

### As a tag on the schema file object in S3
- i.e.: `{'sensitivity': 'PUBLIC'}`

When listing available datasets, it is possible to filter them by tag.

Since it is a desirable feature to be able to filter by sensitivity level, and we can retrieve all objects in AWS with a certain tag
populating a tag with the sensitivity level makes for the fastest way to retrieve this information.

### As a metadata field within the schema file
We have a `/info` endpoint via which the user can retrieve metadata about the dataset. Since the schema acts as this central source of truth
it makes sense to have the sensitivity level alongside the other metadata fields. This also avoids multiple calls to consolidate all the required information.

## Consequences
It is a natural drawback to this approach that the sensitivity information is defined in three separate places.

Ideally these would be consolidated into fewer or just one location, to avoid any divergence or bugs.

Whatever future solution or approach is taken, care should be exercised to ensure that it scales with a large number of schemas.
