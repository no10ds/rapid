# 0007 - Use Parquet as data storage format
Date: 2022-08-26

## Status
Accepted

## Context

Initially, we stored our data in `.csv` format. However, we noticed that when a largely numeric field contains empty values, Athena becomes unable to query it, returning a `HIVE_BAD_DATA` error.

After analysing the problem, it turned out the root cause is the use of the `OpenCSVSerDe` serialisation library which we manually update the Glue table to use. This is because, this library handles custom quote characters.

However, it does not handle null values. Switching to parquet as a data storage format solves this problem.

## Decision

Use Apache Parquet as our data storage format and abandon the `OpenCSVSerDe` serialisation library.

## Consequences

Broadly, the functionality remains unchanged. The only difference is that raw data is stored in `.csv` and partitioned data is stored in `.parquet`.
