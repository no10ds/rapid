# 0005 - Self-Managed Authorisation

Date: 2022-07-19

## Status

Accepted

## People Involved

Lewis Card, Claude Paret, Cristhian Da Silva, Lydia Adejumo, Shashin Dayanand

## Context

Currently, user and client authorisation does not work in a scalable way as both the assigning of credentials and the
groupings of access are separate. Additionally, the user credentials require very granular assignment. Ideally both sets
of credentials would be created and assigned access via the same mechanism.

The current implementation is based on delegating authorisation to Cognito which comes with some limitations, into which
we are running.

Limitations include:
- Maximum 100 client scopes
- Maximum 1000 user groups

The structure of permissions management in Cognito also means that we are forced to use two different permission
structures, which leads to the service needing to distinguish between client and users and therefore have two
authorisation matching mechanisms.

## Decision

We will self-manage authorisation.

This involves:
- Cognito handling authentication (as currently implemented)
- Storing user and client permissions in a self-managed database
- Unifying the authorisation matching mechanism


## Consequences
This will involve re-writing the authorisation layer of the service to handle permissions managed in a custom database.
There will be considerations around backwards compatibility and migration of existing clients/users to use the new approach.
