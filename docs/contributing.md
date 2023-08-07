## Managing The API Environment

`Make` tasks that require the environment to be defined and set-up, will ensure that the latest image has been built and is used for running the task.

If you would like to manually recreate the api environment (e.g.: after speciying a new dependency etc.) you can run `make api-create-image`. This will also output the name of the created Docker image for your convenience.

To create a local virtual environment and install dependencies run `make api-create-local-venv`. This is only used for local development and serves as a workaround in case your IDE cannot use a remote Docker python interpreter.

## Testing

Every rAPId module other than the infrastructure has complementary tests.

### API

To run the API tests locally, you will need to set the following environment variables:

```
DATA_BUCKET=the-bucket
AWS_ACCOUNT=123456
AWS_REGION=eu-west-2
RESOURCE_PREFIX=rapid
DOMAIN_NAME=example.com
COGNITO_USER_POOL_ID=11111111
ALLOWED_EMAIL_DOMAINS=example1.com,example2.com
LAYERS=raw,layer
```

Then run the following command from within the root project directory:

`make api-test`

### UI

To test the UI run the following command from within the root project directory:

`make ui-test`

### SDK

To test the SDK run the following command from within the root project directory:

`make sdk-test`

## Security

### Vulnerabilities

To scan for security vulnerabilities run `make security-check`

We use [bandit](https://pypi.org/project/bandit/) to check for common python vulnerabilities

#### Scanned image vulnerabilities

During deployment, once the image has been pushed to ECR, we automatically scan it for vulnerabilities. The pipeline has
a stage after upload to check the results of the scan and fail if some are found (currently only with high and critical
severity).

AWS also automatically scans the images every day to check for any new vulnerabilities. We have a scheduled pipeline
that checks the results of this scan and fails if the image becomes insecure.

Once you have reviewed the vulnerability, and you deem it acceptable, you can ignore it by adding the `CVE` to a new
line in the `vulnerability-ignore-list.txt` file. Ensure you commit with a meaningful error message, the URL and your
reasoning for ignoring it. By doing this the pipeline will accept that vulnerability and _not_ fail the build.

#### Secrets

We are using the python package [detect-secrets](https://github.com/Yelp/detect-secrets) to analyse all files tracked by
git for anything that looks like a secret that might be at risk of being committed.

There is a `.secrets.baseline` file that defines any secrets (and their location) that were found in the repo, which are
not deemed a risk and ignored (e.g.: false positives)

To check the repo for secrets during development run `make detect-secrets`. This compares any detected secrets with the
baseline files and throws an error if a new one is found.

> Firstly, REMOVE ANY SECRETS!

However, if the scan incorrectly detects a secret, run: `make ignore-secrets` to update the baseline file. **This file
should be added and committed**.

The secret detection step is run as part of the `make precommit` target.

## Releasing

TODO
