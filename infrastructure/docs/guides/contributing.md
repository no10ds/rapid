# Contributing

Guides for developing in this repository

## Initial setup

Configure the custom git hooks location with `make init-hooks`

You will also need to install [terraform-docs](https://terraform-docs.io/). This can be done
with: `brew install terraform-docs`.

## Service Images

We have enabled lifecycle management for the rAPId service images in ECR, [ecr](../../blocks/ecr/main.tf). Our rules:

- Retain up to 10 images that contain a version.
- Retain up to 3 images that do not contain versions.

To change the lifecycle please follow
the [AWS Docs](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html) on lifecycle policies.

## Secrets

We are using the python package [detect-secrets](https://github.com/Yelp/detect-secrets) to analyse all files tracked by
git for anything that looks like a secret that might be at risk of being committed.

Secrets detection is run at pre-commit with a custom hook.

There is a `.secrets.baseline` file that defines any secrets (and their location) that were found in the repo, which are
not deemed a risk and ignored (e.g.: false positives)

To check the repo for secrets during development run `make detect-secrets`. This compares any detected secrets with the
baseline files and throws an error if a new one is found.

⚠️ Firstly, REMOVE ANY SECRETS!

However, if the scan incorrectly detects a secret run: `make ignore-secrets` to update the baseline file. **This file
should be added and committed**.

## Clean up

To clean up all the infra blocks just run `make destroy block={block-to-destroy}`

To clean the dynamically created resources follow [this guide](clean_up_dynamically_created_resources.md)

### Checking your code

To enable automatic pre-commit hook checks:

- Install `pre-commit`, you can follow [pre-commit](https://pre-commit.com/)
- Install `tflint` with e.g.: `brew install tflint`
- At root level, run `pre-commit install`
- To test that it worked, run `pre-commit run --all-files`

This will enable automatic checks before committing any files, giving an extra layer of protection to the code before
being pushed

## Releasing

The guide for how to perform a release of the rapid-infrastructure Terraform.

### Context

The product of the rAPId team is the service image that departments can pull and run in their own infrastructure.

Performing a release fundamentally involves tagging the image of a version of the service with a specific version number
so that departments can reference the version that matches the version
of [rapid-api](https://github.com/no10ds/rapid-api)

⚠️ When releasing a new version of the infrastructure, you must also release a version of
the [service](https://github.com/no10ds/rapid-api) and vice versa. Both versions should be the same (
i.e.: both vX.Y.Z). If there are no changes in one or the other repo, it should still be released along with the other
and a tag added to the same commit as the previous release. This ensures that the version numbers signal the
compatibility between the two elements.

### Prerequisites

- Download the GitHub CLI with `brew install gh`
- Then run `gh auth login` and follow steps

### Steps

1. Decide on the new version number following the [semantic versioning approach](https://semver.org/)

2. Get the commit hash `git rev-parse --short HEAD`

3. Update and commit the [Changelog](../../../changelog.md) (you can follow
   the [template](../../../changelog_release_template.md))
4. Run `make release commit=<commit_hash> version=vX.X.X`
