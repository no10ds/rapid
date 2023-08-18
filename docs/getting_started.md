# Deployment

We provide two options for deploying rAPId within an AWS environment:

1. If you have existing infrastructure (e.g a VPC) that you would like to deploy rAPId within, then you can use the [rAPId module](/infrastructure/deployment/existing/), passing in specific variables relating to your AWS account.
2. If you do not have any exisiting infrastructure, you can instead deploy the [entire rAPId stack](/infrastructure/deployment/full_stack/) creating all the relevant infrastructure.


<!-- TODO: I think getting started should be just about spinning it up, not developing   -->

# Developing


<!-- TODO: This should not be here -->
<!-- Alternatively you can run rAPId locally for development. For more details, please see the [contributing section](/contributing/). -->

## Prerequisites

Install all the required tools

- jq (use Homebrew)
- Git
- [pre-commit](https://pre-commit.com)
- [Make](https://formulae.brew.sh/formula/make)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Homebrew](https://brew.sh/)
- Docker
- [Java version 8+](https://mkyong.com/java/how-to-install-java-on-mac-osx/) (for Batect, future releases will remove this dependency)
- Python (v3.10) - Only for local development without Docker (ideally manage
  via [pyenv](https://github.com/pyenv/pyenv))

Install the pre-commit hooks.

1. In the project root run `make precommit`. This will install all the relevant pre-commit hooks across the entire codebase.

### API

To run the API locally, you will need to set the following environment variables:

```
AWS_ACCOUNT=
AWS_REGION=
COGNITO_USER_POOL_ID=
DATA_BUCKET=
DOMAIN_NAME=
RESOURCE_PREFIX=
ALLOWED_EMAIL_DOMAINS=
```

Then run the following command from within the root project directory:

`make api-run` runs Batect to bring up a locally running version of the api within a Docker container using the base image.

`make api-run-dev` runs Batect to bring up a locally running version of the api within a Docker container using a "hot-reload" mode so you can keep this running during development.

> It is important to note that the app communicates with AWS services and needs to assume the relevant role to do so, however the Docker container **will not have this role**. To run the app locally with an admin context you can assume the admin or user role.

### UI

You can run the UI locally for development either against an already running rAPId instance that has been deployed or a locally running instance of rAPId.

1. Install `npm`, we recommend using [nvm](https://github.com/nvm-sh/nvm)
2. Install the all the required packages `make ui-setup`

To connect the UI with your rAPId instance you will need to set the following environment variables:

```
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_API_URL_PROXY=
```

We provide a proxy system within the UI that allows for API requests to made to the rAPId server without them getting blocked CORS issues. If this setup is required you can set the `NEXT_PUBLIC_API_URL` to some value such as `/myapi` and then your rAPId url within the `NEXT_PUBLIC_API_URL_PROXY` such as `https://myrapid.link`.

`make ui-run-dev` will launch the UI in development mode with hot reloading.

#### Assuming Admin / User Role

As the application connects to AWS services you will need to provide the application with AWS credentials. We recommend using [aws-vault](https://github.com/99designs/aws-vault) to store your AWS credentials. Further instructions to setup aws-vault can be found in the [contributing section](/contributing/#aws-vault-set-up).

1. Assume the relevant role through aws-vault, `aws-vault exec <role>`
2. `printenv` to get the environment variables
3. Add the following environment variables to the root `.env` file of rAPId

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
```
