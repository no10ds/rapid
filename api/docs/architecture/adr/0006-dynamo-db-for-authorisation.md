# 0006 - Dynamo DB for authorisation

Date: 2022-07-26

## Status

Accepted

## People Involved

Lewis Card, Claude Paret, Cristhian Da Silva, Lydia Adejumo, Shashin Dayanand, Jowita Podolak

## Context

We decided to create a self-managed authorisation mechanism [see ADR-0005](./0005-self-managed-authorisation.md),
therefore, we ran an investigation to decide between SQL vs No-SQL DBs from the ones managed by AWS. We took in
consideration the following factors:

- Cost
- Implementation
- Structure
- Use cases
- Scalability
- Features, such as backups, TTL, amongst others

After comparing these considerations between DynamoDB, RDS, Aurora, MariaDB, Oracle in all their flavours (MySQL,
Postgres, Serverless), we found out that:

- DynamoDB is the most cost-effective for our use case.
- DynamoDB is easy to set up and use.
- The relational DBs worked better with our permissions structure design.
- The relational DBs managed the consistency between users and permissions.
- DynamoDB is generally more scalable and has better performance.
- DynamoDB is more accessible (So could be useful for the central hub).
- DynamoDB enables features like Point In Time Recovery and Time To Live with almost no extra cost.
- Since we have an access pattern defined, we don't need another ID to identify the permissions.

## Decision

We will use dynamoDB for our self-managed Authorisation.

## Consequences

- We had to simplify the permissions structure to not use a relation.
- We will be exposing the permissions structure.
- We won't be using an ID for the permissions.
- We will need to handle consistency across the DB ourselves (i.e: deleting existing permissions).
