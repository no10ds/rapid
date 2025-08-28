# E2E Tests

## Setup

Before running the E2E tests, you need to set the following environment variables so that the tests can run against your instance of rAPId.

```
E2E_RESOURCE_PREFIX = #The resource prefix of your rAPId instance
E2E_DOMAIN_NAME = #The domain name that your rAPId instance is hosted at
```

You will also need to be authenticated to the relevant AWS account.

## Running the tests

The tests are run in the deployment pipeline.

To run them locally against the live instance, use:

```bash
make api/test-e2e
```
