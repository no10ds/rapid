<br>
<img src="./logo.png" display=block margin-left=auto margin-right=auto width=80%;/>

# Project rAPId
![Deployment Pipeline](https://github.com/no10ds/rapid/actions/workflows/main.yml/badge.svg)

<a href="https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM"><img src="https://user-images.githubusercontent.com/609349/63558739-f60a7e00-c502-11e9-8434-c8a95b03ce62.png" width=160px; /></a>

# Product Vision

Project rAPId aims to create consistent, secure, interoperable data storage and sharing interfaces (APIs) that enable
departments to discover, manage and share data and metadata amongst themselves.

This will improve the government's use of data by making it more scalable, secure, and resilient, helping to
match the rising demand for good-quality evidence in the design, delivery, and evaluation of public policy.

The project aims to deliver a replicable template for simple data storage infrastructure in AWS, a RESTful API and custom frontend UI to
ingest and share named, standardised datasets.

# Tech Stack

- Python
- FastApi
- Docker
- AWS (ECR, ECS, EC2, S3, Glue, Athena, Cognito, DynamoDB)
- Terraform
- Github Actions
- Typescript
- NextJS

# Deploying a rAPId Instance

Please reach out to us on [slack](https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM) if you would like the rAPId team to deploy and manage a rAPId instance on your behalf.

Or you can consult the [Infrastructure Repo](https://github.com/no10ds/rapid/tree/main/infrastructure) for guidance on how to spin up an instance yourself.

# Developing

This is a quick guide to running rAPId locally for development.
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

## Monorepo

The rapid repository is a monorepo containing all the different rapid services and products.
