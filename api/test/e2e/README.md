# E2E Tests

## Initial Setup

The E2E tests require some first time setup. The tests will hit the real endpoints and some validation checks are
performed that require the relevant resources to be available in AWS (files in S3, Crawlers, Glue Tables, etc.).

### Data setup

Run [this](./setup_e2e_tests.py) script, passing in values for the environment variables listed below.

``` bash
CLIENT_ID
CLIENT_SECRET
BASE_URL
```

> Note: After running this it will take a few minutes for the uploaded data to become available and for the tests to pass.

## Running the tests

The tests are run in the deployment pipeline.

To run them locally against the live instance, use:

```bash
make test-e2e
```

## Gotchas

If some tests return an HTTP status of 429, this is due to crawlers still running (or in their stopping phase). This
generally happens when the E2E tests are run multiple times in quick succession. Wait for the crawlers to finish and
re-run the tests.
