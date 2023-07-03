# Developer Usage Guide

This usage guide is aimed at developers maintaining the rAPId service.

## Overview of application

The core concept of the application is the upload and querying of data. The intention is that different departments will
run their own instance of the application.

The data that users upload is organised by `domain`, `dataset` and `version`.

`Domain` - Some higher level categorisation of multiple datasets, e.g.: `road_transport`, `border`, etc.
`Dataset` - The individual dataset name as it exists within the domain, e.g.: `electric_vehicle_journeys_london`
, `confirmed_visa_entries_dover`, etc.
`Version` - Automatically generated version of the schema/data that is uploaded, e.g.: `1`, `2`.

### Usage flow

This section lays out what happens at different stages when using the application. Although high-level, this should help
to clarify the overarching structure and where to look when things go wrong.

1. Application service spins-up
    1. No domains or datasets exist
2. Client app/user registered and given desired permissions
3. Client app uploads schema to define the first dataset
4. User logs in to the UI
5. User uploads dataset file
6. AWS Glue Crawler runs to look at the data and construct table in the Glue Catalog
7. The data is available to be queried

## Authorisation flows

Two main flows are currently supported:

- Client app
- User

The client app is a programmatic client that is intended as the main way to interact with the API. Client apps are
currently able to log into and use the `/docs` page and to use the API by programmatic means (custom app, script, cURL,
Postman, etc.)

The user is a human element that uses the custom UI.

| Flow       | Token        | Auth method | Permission example             | Notes                                                            |
|------------|--------------|-------------|--------------------------------|------------------------------------------------------------------|
| User       | User Token   | Permissions | `WRITE_PUBLIC`, `READ_PRIVATE` | No specificity at the domain or dataset level, only sensitivity  |
| Client app | Client Token | Permissions | `WRITE_PUBLIC`, `READ_PRIVATE` | No specificity at the domain or dataset level, only sensitivity  |

The "action" component of a permission (`READ`, `WRITE`, etc.) is used only in the matching logic when a request is made
and compared to the specified permission assigned to the endpoint being accessed.


## Handling Exceptions

We have a global exception handler that catches custom defined and unexpected exceptions. This handler either redirects
the user to an error page if it is a browser request or otherwise returns a structured json response with corresponding
status code.

When handling exceptions in the code favour using the most generic custom exceptions as defined in `custom_exceptions.py`.
Only create a new custom exception if you need it to modify behaviour further up in the call chain and this would improve readability.
