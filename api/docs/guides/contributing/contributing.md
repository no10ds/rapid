# Contributing

## Familiarisation 🧊

Familiarise yourself with the following documentation:

1. [Developer usage guide](dev-usage.md)
2. [Application context](application_context.md)
3. [ADRs](../../architecture/adr/)
4. [Infrastructure guides](https://github.com/no10ds/rapid-infrastructure)
5. [Application limitations](application_limitations.md)
5. [Future improvements](improvements.md)

## aws-vault set up

We recommend using aws-vault to handle the different aws credentials. Details on how to set it up and run can be found [here](https://github.com/99designs/aws-vault).

## Developing 🤓

### Managing the environment

`Make` tasks that require the environment to be defined and set-up, will ensure that the latest image has been built and
is used for running the task.

If you would like to manually recreate the environment (e.g.: after specifying a new dependency etc.) you can
run `make create-runtime-env`. This will also output the name of the created Docker image for your convenience.

To create a local virtual environment and install dependencies run `make create-local-venv`. This is only used for local
development and serves as a workaround in case your IDE of choice cannot use a remote Docker python interpreter. Ensure
you remember to activate the `venv` once it has been created.

To clean your workspace run `make clean-env`. Currently, this removes the virtual environment, environment image, pytest
caches and coverage reports.

### Dependency management

Batect will build the Docker image with all relevant dependecies baked in. No input on your part will be required.

To install all dependencies, if you are using a local `venv` simply activate the virtual environment and
run `pip install -r requirements.txt`.

To add a new dependency, if you are using a local `venv` simply activate the virtual environment and
run `pip install <dependency>` and freeze this into the requirements file: `pip freeze > requirements.txt`

### General maintenance

You can run `make shell` to run commands in a clean environment against the mounted local source code; e.g.: Install
dependencies, etc

## Testing

To run the tests in your IDE ensure that the test runner's working directory is set to the root directory of the
project.

For PyCharm, go to `Run Configurations > Edit Configurations > Edit Configuration Templates > Python Tests`
Then, edit the `Working Directory` field of BOTH the `Autodetect` and `pytest` configuration templates to be the
absolute path to the root project directory e.g.: `/Users/user/Documents/rapid-api`

You will need to add some environment variables to your run configuration templates too (with sample values below):

- `DATA_BUCKET=the-bucket`
- `AWS_ACCOUNT=123456`
- `AWS_REGION=eu-west-2`
- `RESOURCE_PREFIX=rapid`
- `DOMAIN_NAME=example.com`
- `COGNITO_USER_POOL_ID=11111111`
- `ALLOWED_EMAIL_DOMAINS=example1.com,example2.com`
- `LAYERS=raw,layer`

We use pytest as our test runner. This can be run by calling

`make test`

### Scripts

There are currently four scripts located in the `test/scripts`, these are:

- Delete Protected Domain Permission
- User Permission Test
- Migrate Datasets to Schema Versioning
- v5.0.0 Schema Migration
- v6.0.0 Domain Case Insensitive

#### Delete Protected Domain Permission

The protected domain permission was created to easily remove the protected permission from the database and all
protected datasets associated with that domain. This is due to the prerequisite of uploading a protected dataset which
requires a protected domain permission to exist. In order to run this script one would need to specify the domain to be
deleted.

```commandline
python test/scripts/delete_protected_domain_permission domain-to-be-deleted
```

#### Migrate Datasets to Schema Versioning

rAPId v3.0.0 introduced the ability to version dataset schemas. This introduced a breaking change and running the migration script updates previous datasets to the required new v3.0.0 compatible.

```commandline
python test/scripts/migrate_datasets_to_new_versioning_structure.py
```

### v5.0.0 Schema Migration

rAPId v5.0.0 introduced a new search over data metadata as part of introductionary work into a data catalog. The data catalog search introduces a breaking change as the current pretty-printed schemas are not compatiable for searching within Athena. The v5.0.0 migration script removes the pretty-printed format from the saved schemas.

```commandline
python migrations/scripts/v5_schema_migration.py
```

### v6.0.0 Domain Case Insensitive

rAPId v6.0.0 made domains case insensitive. This was a design decision but also helped clear up some core issues around permissions. For instance you could create a protected domain with a domain uppercase and the exact same protected domain with a domain lowercase would not get picked up by the uppercase. The v6.0.0 migration script migrates over all non-lowercase domains.

```commandline
python migrations/scripts/v6_domain_case_insensitive.py
```

### Checking your code

`make precommit` will lint source code, check for secrets and security vulnerabilities, validate config and run tests

To enable automatic pre-commit checks:

- Install `pre-commit`, you can follow [pre-commit](https://pre-commit.com/)
- At root level, run `pre-commit install`
- To test that it worked, run `pre-commit run --all-files`

This will enable automatic checks before committing any files, giving an extra layer of protection to the code before
being pushed

### Security

#### Vulnerabilities

To scan for security vulnerabilities run `make security`

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

> ⚠️ Firstly, REMOVE ANY SECRETS!

However, if the scan incorrectly detects a secret, run: `make ignore-secrets` to update the baseline file. **This file
should be added and committed**.

The secret detection step is run as part of the `make precommit` target.

#### Formatting

To format the code or check for linting errors we use `black` and `flake8`. Use the make targets for convenience:

`make format`

`make lint`

## Deployment and Infrastructure 🚀

Service infrastructure is stored in a [separate repository](https://github.com/no10ds/rapid-infrastructure).

See README and docs in that repository for more details

### Pipeline

We are using Github Actions as the pipeline solution, with a self-hosted runner hosted in AWS.

The config for the pipeline is in `.github/workflows/main.yaml`

#### Image tagging

As the code moves through the pipeline and passes or fails successive checks, the built image is tagged accordingly.

1. Initially all images are tagged with their `<commit-hash>`
2. If the image vulnerability scan check stage finds issues, the image is tagged with `VULNERABLE-<commit-hash>` and the
   deployment aborts
3. If no vulnerabilities are found, a subsequent pipeline stage tags the image as `PROD`
4. During deployment, the ECS Task Definition looks for the latest image tagged with `PROD` and deploys it
5. Subsequent taggings of new deployment candidates simply override the previous `PROD` tag

## Releasing

The guide for how to perform a release of the service image.

### Context

The product of the rAPId team is the service image that departments can pull and run in their own infrastructure.

Performing a release fundamentally involves tagging the image of a version of the service with a specific version number
so that departments can reference the version they want when pulling from ECR.

⚠️ When releasing a new version of the service, you must also release a version of
the [infrastructure](https://github.com/no10ds/rapid-infrastructure) and vice versa. Both versions should be the same (
i.e.: both vX.Y.Z). If there are no changes in one or the other repo, it should still be released along with the other
and a tag added to the same commit as the previous release. This ensures that the version numbers signal the
compatibility between the two elements.

### Prerequisites

- Download the GitHub CLI with `brew install gh`
- Then run `gh auth login` and follow steps

### Steps

1. Decide on the new version number following the [semantic versioning approach](https://semver.org/)
2. Update and commit the [Changelog](../../../changelog.md) (you can follow
   the [template](../../../changelog_release_template.md))
3. Run `make release commit=<commit_hash> version=vX.X.X`

> ⚠️ Ensure the version number follows the format `vX.X.X` with full-stops in the same places

Now the release pipeline will run automatically, build the image off that version of the code, tag it and push it to ECR

### How to add security to an endpoint

We are using the FastApi Security package. Security takes dependencies and scopes as arguments. In our case the
dependency are the ```secure_endpoint```, ```secure_dataset_endpoint``` methods, and one or more of the following action
permissions:

- `READ`
- `WRITE`
- `DATA_ADMIN`
- `USER_ADMIN`

For instance, if `WRITE` permission is used, that means that whoever is trying to access the endpoint needs to have any
of `WRITE_ALL`, `WRITE_<sensitivity_level>`, `WRITE_PROTECTED_{DOMAIN}`  listed in their permissions, where sensitivity level is the sensitivity
level of the dataset being modified. Otherwise, the request fails.

> ⚠️ ️NOTE: Higher sensitivity levels imply lower sensitivity levels.

To add security to the endpoint, add specify the `dependencies=` keyword argument and specify the permissions in the
endpoint annotation as listed in the examples below:

* For endpoints **without** ```domain``` and ```dataset``` in the url path, use the dependency ```secure_endpoint```:

```
@app.post("/schema", dependencies=[Security(secure_endpoint, scopes=[Action.READ])])
```

or

* For endpoints **with** ```domain``` and ```dataset``` as part of the url path, use the
  dependency ```secure_dataset_endpoint```:

```
@app.get("/{domain}/{dataset}/info",
                     dependencies=[Security(secure_dataset_endpoint, scopes=[Action.READ])])
```

### How to add security to the endpoint - Front End Layer

Some pages in the frontend layer are only accessible after the user has authenticated, e.g.: the `/upload` page. In
order to protect them, the dependency functions ```secure_endpoint``` and ```secure_dataset_endpoint``` should be
included in the Fast API endpoint annotation as described in the example below:

```
@app.get("/upload", include_in_schema=False,
         dependencies=[Depends(secure_dataset_endpoint)])
```

Note that ```secure_dataset_endpoint``` dependency function must be used when ```domain``` and ```dataset``` is present
in the url path and should be taken in consideration to determine the permission to access.

When using the frontend layer instead of the client app token, the user token is used. This token contains Cognito user
subject id which can be looked up in the permissions database to describe the permission access level for that
particular user. The database follows a naming convention of ```WRITE_PUBLIC```.

## Gotchas 🤯

- When using `Pyenv` you will probably be using v2+. If this is the case, ensure you add `$(pyenv root)/shims` to your
  PATH and NOT `$(pyenv root)/bin`.
- If you find yourself needing to delete a Data Catalog table, and it is failing silently, ensure you have set an Output
  Location for the results (an S3 bucket).
- If you need to delete a tag run `git tag -d <tag_name>` to delete the tag locally. Then
  run `git push --delete origin <tag_name>` to delete the remote one.
- The release pipeline will only run if the tagged commit contains the relevant workflow config file. That is, you
  cannot commit a workflow config file now and run a previous version of the codebase that does not have that file
  through the pipeline.
- If you need to return csv content from the API, you need to use Response object (PlainTextResponse specifically)
  instead of returning a string.
- When logging out the "Rapid Access Token" will be deleted from the session, however, the cognito session remains and
  clicking in "login" will authenticate the same user automatically.
