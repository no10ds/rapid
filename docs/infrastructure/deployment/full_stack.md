For teams with no existing infrastructure and just a blank AWS Account, we have ```make``` commands that will set up the necessary infrastructure from scratch with sensible defaults.

## Pre-requisites

Most of the infrastructure is managed by Terraform, to be able to run these blocks, please [install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).

Our infrastructure is built using AWS, so you'll need an AWS account, and access to the cli to run the project. You will need to create a named profile (We suggest 'gov').

Follow these steps to set up the AWS profile:

- [Install/Update AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Set up a named profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) if you already have the AWS cli.

After setting up the named profile, the current session can be checked by running ```aws sts get-caller-identity```. We have a file (`scripts/env_setup.sh) with the required exports to use the 'gov' profile. These exports have to be run when starting a new session.

We use `jq` in our scripts to help the `make` targets work correctly, please [Install jq](https://stedolan.github.io/jq/download/) before running any make command.

## Infrastructure Configuration

There are two config files needed to instantiate the rAPId service, they are `input-params.tfvars` and `backend.hcl`. Please create these with the templates provided, we will add the content shortly.

`input-params.tfvars` template:

```
state_bucket = ""
data_bucket_name = ""
log_bucket_name = ""
iam_account_alias = ""

application_version = ""
ui_version = ""
domain_name = ""
aws_account = ""
aws_region = ""
resource-name-prefix = "rapid"
ip_whitelist = []
# Please fill with the hosted zone id linked to the domain,
# otherwise a new hosted zone will be created from scratch
hosted_zone_id = ""
# Please fill with the certificate arn linked to the domain,
# otherwise a new certificate will be created and attached
certificate_validation_arn = ""

support_emails_for_cloudwatch_alerts = []

tags = {}
```

`backend.hcl` template:

```
bucket="REPLACE_WITH_STATE_BUCKET"
region="REPLACE_WITH_REGION"
dynamodb_table="REPLACE_WITH_LOCK_TABLE"
encrypt=true
```

By default, the files are expected to be inside a folder called `rapid-infrastructure-config` and positioned on your local machine relative to rapid-infrastructure as shown below:

```
├── rapid
│   └── infrastructure
│       ├── blocks
│       ├── modules
│       └── etc...
├── rapid-infrastructure-config
│   ├── input-params.tfvars
│   └── backend.hcl
```

If you wish to use a different location, then please run:

```
export RAPID_INFRA_CONFIG_ENV=../my/relative/location/to/rapid/infrastructure
```

If you want to share your infrastructure values across your team then you can turn `rapid-infrastructure-config` into a private repo.

## First time, one-off setup (backend)

The first step is to set up an S3 backend so that we can store the infra-blocks' state in S3 and rely on the DynamoDB lock
mechanism to ensure infrastructure changes are applied atomically.

To set up the S3 backend follow these steps:

- Replace the values in `backend.hcl` with your custom values (these can be any value you would like). They will be referenced to create the Terraform state components and used going forwards as the backend config.
- In the root folder run ```make infra-backend```, this will initialise Terraform by creating both the state bucket and dynamodb table in AWS.

## IAM User Setup (Optional)

This module is used to set the admin and user roles for the AWS account. It ensures a good level of security by expiring credentials quickly and ensuring that MFA is always needed to refresh them.

> CAUTION: If you have existing AWS users and don't include them as part of the manual_users, this block will remove them!

You will need define the desired IAM users (both new and previous manually added
ones) in `input-params.tfvars` and deploy the [iam-config](#deploying-remaining-infra-blocks) block with admin privileges. After that you can use [assume-role](#assume-role) to perform infrastructure changes.

`infra-params.tfvars` snippet for 'user1':

```
set_iam_user_groups = ["users", "admins"]

iam_users = {
  user1 = {
    groups = ["users", "admins"]
  }
}

manual_users = {
  "user1@domain.email" = {
    groups = ["users", "admins"]
  }
}
```

## Assume role

In order to gain the admin privileges necessary for infrastructure changes one needs to assume admin role. This will be
enabled only for user's defined in `input-params.tfvars`, only after logging into the AWS console for the first time as an
IAM user and enabling MFA.

Then, to assume the role, set up the profile (`scripts/env_setup.sh`), run ```make infra-assume-role``` and follow the prompts.

## Deploying remaining infra-blocks

Once the state backend has been configured, provide/change the following inputs in `input-params.tfvars`.

Required:

- `state_bucket` - The name of the state bucket, as defined in `backend.hcl`
- `data_bucket_name` - This will be the bucket where the data is going to be stored, it needs to be a unique name.
- `log_bucket_name` - This is the bucket that will be used for logging, it needs to have a unique name.
- `iam_account_alias` - account alias required by AWS, it needs to be a unique name
- `application_version` - service's docker
  image version
- `ui_version` - Static UI version
- `domain_name` - application hostname ([can be a domain or a subdomain](/infrastructure/domains_subdomains/))
- `aws_account` - aws account id where the application will be hosted
- `aws_region` - aws region where the application will be hosted
- `iam_users` - IAM users to be created automatically, with roles to be attached to them
- `manual_users` - IAM users that has been already created manually, with roles to be attached. (Can be left empty)
- `set_iam_user_groups` - User groups that need to be present on each user. (i.e. if the value is set to admin, then all
  the users will require the admin role)
- `support_emails_for_cloudwatch_alerts` - list of engineer emails that should receive alert notifications [more info](/infrastructure/alerting_monitoring/)
- `ip_whitelist` - ip range to add to application whitelist. The expected value is a list of strings.

Optional:

- `resource-name-prefix` - prefix value for resource names, can be left as rapid
- `hosted_zone_id` - if provided, will add an alias for the application load balancer to use the provided domain using
  that HZ. Otherwise, it will create a HZ and the alias
- `certificate_validation_arn` - if provided, will link the certificate to the load-balancer https-listener. Otherwise,
  will create a new certificate and link it. ([managing certificates](/infrastructure/certificates/)
- `tags` - if provided, it will tag the resources with the defined value. Otherwise, it will default to "Resource = '
  data-f1-rapid'"

Then, run the following command on each block:

- ```make infra-init block=<block-name>``` to initialise Terraform
- ```make infra-plan block=<block-name>``` to plan (to check the changes ensuring nothing will be run)
- ```make infra-apply block=<block-name>``` to apply changes, when prompted type ```yes```

Run the blocks in this order:

1. [iam-config](#iam-user-setup-optional)
> All the users' roles/policies will be handled here and will delete any previous config
2. vpc
3. s3
4. auth
5. data-workflow
6. app-cluster
7. ui
