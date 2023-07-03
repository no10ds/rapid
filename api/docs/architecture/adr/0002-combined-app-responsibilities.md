# 0002 - Combined App Responsibilities
Date: 2022-03-02

## Status
Accepted

## Context

In order to provide a frontend to users with which to upload files rather than the OpenAPI docs that come out of the box with FastAPI,
we need to decide which avenue we pursue to implement this.

Several approaches are available:
- A separate SPA (React, Angular, Vue, etc.) that calls the existing backend API
- Using the built-in templating engine and responses with FastAPI and Starlette


## Decision
We decided to use the built-in templating engine and responses with FastAPI and Starlette

This is due to:
- Time constraints
- Simplicity of implementation
- Team familiarity with approach

## Consequences
Implementing the frontend portion of the app alongside the REST API portion results in a split in the responsibilities of the application.

### Endpoint implications
We now have:
- A set of endpoints that function as a REST API and return JSON responses
- A set of endpoints that function as the frontend and return HTML responses

### Authorisation implications
All protected endpoints, regardless of whether they are for the REST API or frontend, check for an access token.

There are two ways to provide a token:
1. User token set in the browser as a cookie
2. Client app token provided in the `Authorization` header

All protected endpoints are protected by one central authorisation method.

This authorisation method is responsible for:
- distinguishing the source of the request (browser vs. programmatic client)
- retrieving the token from the appropriate place
- matching relevant permissions (via `scope` or `group` fields in the token)

> ⚠️ We do not support logging in to the OpenAPI docs (`/docs`) as a user. Only the client app flow is supported. This is due to limitations of FastAPI, OAuth2 and Cognito
