<br>
<img src="./logo.png" display=block margin-left=auto margin-right=auto width=60%;/>

# Project rAPId
![Deployment Pipeline](https://github.com/no10ds/rapid-api/actions/workflows/main.yml/badge.svg)

<a href="https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM"><img src="https://user-images.githubusercontent.com/609349/63558739-f60a7e00-c502-11e9-8434-c8a95b03ce62.png" width=160px; /></a>

# Product Vision 🔭

Project rAPId aims to create consistent, secure, interoperable data storage and sharing interfaces (APIs) that enable
departments to discover, manage and share data and metadata amongst themselves.

This will improve the government's use of data by making it more scalable, secure, and resilient, helping to
match the rising demand for good-quality evidence in the design, delivery, and evaluation of public policy.

The project aims to deliver a replicable template for simple data storage infrastructure in AWS, a RESTful API and custom frontend UI to
ingest and share named, standardised datasets.

# Tech Stack 🍭

- Python
- FastApi
- Docker
- AWS (ECR, ECS, EC2, S3, Glue, Athena, Cognito, DynamoDB)
- Terraform
- Github Actions

# Deploying a rAPId Instance

Please reach out to us on [slack](https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM) if you would like the rAPId team to deploy and manage a rAPId instance on your behalf.

Or you can consult the [Infrastructure Repo](https://github.com/no10ds/rapid-infrastructure) for guidance on how to spin up an instance yourself.

# Developing

This is a quick guide to running rAPId locally for development. For greater details please see the [Contributing README](docs/guides/contributing/contributing.md)

## Prerequisites

Install all the required tools
- jq (use Homebrew)
- Git
- [pre-commit](https://pre-commit.com)
- [Make](https://formulae.brew.sh/formula/make)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Homebrew](https://brew.sh/)
- Docker (from Self Service)
- [Java version 8+](https://mkyong.com/java/how-to-install-java-on-mac-osx/) (for Batect (future releases will remove
  this dependency))
- Python (v3.10) - Only for local development without Docker (ideally manage
  via [pyenv](https://github.com/pyenv/pyenv))

Install the pre-commit hooks.

1. In the project root run `make precommit`. This will create the relevant Docker image with all the dependencies with which to run subsequent tasks and the app locally.

## Running Locally 🏃‍♂️

To run the app locally, you will need to set the following environment variables:

```
AWS_ACCOUNT=
AWS_REGION=
AWS_DEFAULT_REGION=
COGNITO_USER_POOL_ID=
DATA_BUCKET=
DOMAIN_NAME=
RESOURCE_PREFIX=
ALLOWED_EMAIL_DOMAINS=
```

`make run` runs batect to bring up a locally running version of the application within a Docker container using the base image.

`make run-dev` runs batect to bring up a locally running version of the application within a Docker conrainer un a "hot-reload" mode so you can keep this runnning during development.

> ⚠️ Note that the app communicates with AWS services and needs to assume the relevant role to do so, however the Docker container **will not have this role**.
>
>
> To run the app locally with an admin context you can assume the admin or user role

## Assuming Admin / User Role

We recommend using [aws-vault](https://github.com/99designs/aws-vault) to store your AWS credentials.

1. Follow the instructions to [setup aws-vault](docs/guides/contributing/contributing.md#aws-vault-set-up)
2. Assume the relevant role through aws-vault
3. `printenv` to print out the AWS tokens
4. Add the following environment variables to the root `.env` file of rAPId

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
```

Now in order to log in, the application will need the relevant session token for Cognito authentication. Login to your live deployed version of rAPId. Then in the Browser developer tools look for a cookie called `rat`. Copy the contents of this token into the cookie running at localhost. Refresh and you will see rAPId has assumed you have logged in now.

## Session timeout

By default a 5 minute timer has been addedd to the user session in the UI. This means after the 5 minutes of inactivity the `rat` cookie will be removed and a new one will have to be created and copied.

When developing locally it is recommended to extend this timeout. To change this value go to [session_time.js](./templates/js/session_timer.js) and change the `FIVE_MINUTES` field. **It is important not to commit this change when pushing changes.**

# Using the rAPId service 🙋

Please see the [usage guide](docs/guides/usage/usage.md)

# High Level Architecture 🏡

Diagrams are compiled [here](docs/architecture/C4_diagrams) and show the architecture of the service
