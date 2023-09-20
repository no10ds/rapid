# Migration

## Migrating to v7 from v6

All of the datasets need to be moved to a layer as part of the v7 migration.

The migration script carries this out, along with other operations.

To execute it, you'll need to decide:

1. Which layer the existing datasets should be moved to.
2. What the full complement of layers in your rAPId instance should be.

### Prerequisites

#### Infrastructure changes

The v7.0.0 infrastructure changes need to be applied to your rAPId instance.

Update the version of the rAPId terraform module that you are using and apply the terraform.

#### Local requirements

You will need the ability to run `Batect`, the requirements for which are listed [here](https://batect.dev/docs/getting-started/requirements/).

### Steps:

#### Make the infrastructure changes

The v7 infrastructure changes need to be applied to your rAPId instance.

1. Add the `layers` variable to the rAPId cluster module. `layers` will be a list of the layers you wish to use in your rAPId instance. You can omit this if you just want to use the `default` layer.
2. Change the rAPId module source to:
   `git@github.com:no10ds/rapid.git//infrastructure/modules/rapid`
3. Update both the application_version and ui_version variables to `v7.0.4`

Apply these changes.

#### Clone the repo

To do this, run:

`git clone -b v7.0.4 git@github.com:no10ds/rapid.git`

#### Set your environment variables

Within the rAPId repo, set the following variables in the `.env` file to match those of your rAPId instance and AWS account:

```
# rAPId instance variables
- AWS_REGION=
- DATA_BUCKET=
- RESOURCE_PREFIX=

# AWS environment variables
- AWS_ACCESS_KEY_ID=
- AWS_SECRET_ACCESS_KEY=
- AWS_SESSION_TOKEN=
```

#### Run the migration script

You can now run the script and specify your layer configuration. Examples for it are below:

##### Example 1:

You do not wish to use the layer functionality:

- The existing datasets can be moved to a `default` layer
- The full complement of layers can just consist of one, called `default`.

To do this, you would run:

```
make migrate-v7 layer=default all-layers=default
```

##### Example 2:

You wish to use the layer functionality and largely have raw data already in your rAPId instance:

- The existing datasets can be moved to a `raw` layer.
- The full complement of layers in your rAPId instance can mirror your architecture and be: `raw`, `curated` and `presentation`

To do this, you would run:

```
make migrate-v7 layer=raw all-layers=raw,curated,presentation
```
