## Prerequisites

### Install the dependencies

- Git
- [Make](https://formulae.brew.sh/formula/make)
- [Homebrew](https://brew.sh/)
- Docker

Use brew to install the rest of the dependencies and setup the pre-commit hooks by running:

```
make setup
```

## Running the API

To run the API locally, you will need to set the following environment variables. They will correspond to rAPId resources already created in AWS and can be taken from the environment of your rAPId ECS task:

```
AWS_ACCOUNT=
AWS_REGION=
COGNITO_USER_POOL_ID=
DATA_BUCKET=
DOMAIN_NAME=
RESOURCE_PREFIX=
ALLOWED_EMAIL_DOMAINS=
```

You can then run the following commands from within the root project directory:

- `make python-setup` - Installs and selects the correct version of Python with pyenv.

- `make backend/setup` - Creates the virtual environment for the API and pip installs the Python dependencies.

- `make api/run` - Runs the API in development mode

## Passing an AWS Role

As the application connects to AWS services you will need to provide the application with AWS credentials.

The AWS credentials need to be present as environment variables, wherever you are running the application from.

For security, we recommend that these are only the temporary credentials of an assumed role.

## Running the Frontend

You can run the Frontend locally for development either against an already running rAPId instance that has been deployed or a locally running instance of rAPId.

1. Install the correct version of node with nvm by running `make node-setup`
2. Install the all the required packages `make frontend/setup`

To connect the Frontend with your rAPId instance you will need to setup two environment variable files, both within `./frontend`:

### 1. .env.local

The Frontend uses a proxy system that allows API requests to be made to the rAPId server without them getting blocked CORS issues. You can set the `NEXT_PUBLIC_API_URL` to the api suffix of the rAPId instance `/api` and set `NEXT_PUBLIC_API_URL_PROXY` to be the full domain name, such as `https://myrapid.co.uk`.

```
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_API_URL_PROXY=
```

### 2. .env.development

This file allows you to set the `client_id` and `client_secret` that your locally running Frontend can use to authenticate to the API instance that it is running against. They are in this separate file so that they do not get packaged at build time and with the app and stay secret.

```
FRONTEND_CLIENT_ID=
FRONTEND_CLIENT_SECRET=
```

Running `make frontend/run-dev` will then launch the Frontend in development mode with hot reloading.

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

`make api/test`

### Frontend

To test the Frontend run the following command from within the root project directory:

`make frontend/test`

### SDK

To test the SDK run the following command from within the root project directory:

`make sdk/test`

## Security

#### Code vulnerabilities

To scan for security vulnerabilities run `make security-check`

[bandit](https://pypi.org/project/bandit/) is in use to check for common python vulnerabilities.

#### Infrastructure flaws

To launch a static scan on the infrastructure, you can run `make infra/scan`.

[checkov](https://www.checkov.io/) is used to check for flaws in the AWS architecture.

#### Scanned image vulnerabilities

The API image is scanned on a daily basis for vulnerabilities. New releases cannot then be made until image the vulnerabilities are addressed.

To address the vulnerability, reviewed the content of it and assess if the application is likely to be affected by it.

If it is deemed to be acceptable, you can ignore it by adding the `CVE` to a new
line in the `vulnerability-ignore-list.txt` file. Ensure you commit with a meaningful error message, the URL and your
reasoning for ignoring it. By doing this the pipeline will accept that vulnerability and _not_ fail the build.

If the vulnerability is not acceptable, then another base image will need to be used.

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

rAPId has several core components that are all versioned when a release is created:

1. A API image that can be pulled to run the python application.
2. A zip package containing the static Frontend.
3. A public pypi package of the built rAPId-sdk that provides an easy and pythonic way to interact with the API.
4. A terraform module that can be used to create the AWS services necessary for running the various components of rAPId.

Performing a release involves tagging the repository with a new version number so that the API image, Frontend, SDK and Terraform all get versioned. Note that the API and SDK can be versioned and released independently, so you can conserve the API version number if just releasing an update to the SDK.

### Prerequisites

- Run `gh auth login` and follow the steps

### Steps

1. Decide on the new version number for the API and the Frontend and/or the SDK following the [semantic versioning approach](https://semver.org/).
2. Update and commit the Changelog (you can follow
   the [template](https://github.com/no10ds/rapid/blob/main/changelog_release_template.md)). You'll need to separate SDK and API changes into their respective changelogs, under docs/changelog.
   1. Bundle API, Frontend and terraform changes as part of the API changelog.
   2. Insert SDK changes into the SDK changelog.
3. Run `make release commit=<commit_hash> type=<sdk|api> version=vX.X.X`

> Ensure the version number follows the format `vX.X.X` with full-stops in the same places for both API and SDK changes.

Now the release pipeline will run automatically, build all images and packages off that version of the code and tag it within GitHub.
