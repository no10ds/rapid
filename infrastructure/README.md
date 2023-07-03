# rAPId infrastructure

<img src="https://github.com/no10ds/rapid-api/blob/main/logo.png?raw=true" display=block margin-left= auto margin-right=auto width=80%;/>

The rAPId service allows users to ingest, validate and query data via an API. This repo provides a self-service
mechanism to deploy the rAPId service either on top of your existing infrastructure or from scratch.

<br />
<p align="center">
<a href="https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM"><img src="https://user-images.githubusercontent.com/609349/63558739-f60a7e00-c502-11e9-8434-c8a95b03ce62.png" width=160px; /></a>
</p>

## Getting started

If you are looking to develop in this repository also take a look at the [contributing readme](docs/guides/contributing.md)

- Deploy rAPId service
  - [Deploy the rAPId module (On top of your existing Terraform infrastructure)](#deploy-service-modules)
  - [Deploy the full stack (If you don't have existing Terraform infrastructure)](#deploy-full-stack)

## Infrastructure diagrams

- The bootstrapping steps described below are also represented as a
[diagram](./docs/diagrams/infrastructure/infrastructure_bootstrapping.svg)
- For all the infrastructure
diagrams [see files here](./docs/diagrams/)

## Contact us

Please reach out to us on [slack](https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM).

## Deploy the rAPId module

For departments that already have an existing infrastructure, we have extracted the top level infrastructure into a single Terraform [module](./modules/rapid/).

Usage:

```
module "rapid" {
  source  = "git@github.com:no10ds/rapid-infrastructure.git//modules/rapid"

  # Account details
  aws_account = ""
  aws_region  = ""

  # Application hosting
  domain_name = ""
  ip_whitelist = ""
  public_subnet_ids_list = [""]
  private_subnet_ids_list = [""]
  vpc_id = ""

  # Resource naming - must be unique
  resource-name-prefix = "rapid-${your-team-name}"

  # Support
  support_emails_for_cloudwatch_alerts = [""]

  # ..... etc.
}
```

Provide the required inputs as described:

- `aws_account` - AWS account where the application will be hosted
- `aws_region` - AWS region where the application will be hosted
- `domain_name` - Application hostname ([can be a domain or a subdomain](#managing-domainssubdomains))
- `ip_whitelist` - A list of IP addresses that are allowed to access the service.
- `public_subnet_ids_list` - List of public subnets for the load balancer
- `private_subnet_ids_list` - List of private subnets for the ECS service
- `vpc_id` - VPC id
- `resource-name-prefix` - The prefix that will be given to all of these rAPId resources, it needs to be unique so to not conflict with any other instance e.g `rapid-<your-team/project/dept>`
- `support_emails_for_cloudwatch_alerts` - List of engineer emails that should receive alert notifications

There are also these optional inputs:

- `application_version` - The service's image [version](https://github.com/no10ds/rapid-api/blob/master/changelog.md)
- `ui_version` - The static UI [version](https://github.com/no10ds/rapid-ui/blob/master/CHANGELOG.md)
- `hosted_zone_id` - If provided, will add an alias for the application load balancer to use the provided domain using that HZ. Otherwise, it will create a HZ and the alias
- `certificate_validation_arn` - If provided, will link the certificate to the load-balancer https-listener. Otherwise, will create a new certificate and link it. ([managing certificates](#managing-certificates))
- `app-replica-count-desired` - if provided, will set the number of desired running instances for a service. Otherwise,
  it will default the count to 1
- `app-replica-count-max` - if provided, will set the number of maximum running instances for a service. Otherwise, it
  will default the count to 2
- `catalog_disabled` - if set to `true` it will disable the rAPId internal data catalogue
- `tags` - if provided, it will tag the resources with the defined value. Otherwise, it will default to "Resource = '
  data-f1-rapid'"

Once you apply the Terraform, a new instance of the application should be created.

## Deploy full stack

For teams with no existing infrastructure and just a blank AWS Account, we have ```make``` commands that will set up the necessary infrastructure from scratch with sensible defaults.

### Pre requisites

Most of the infrastructure is managed by Terraform, to be able to run these blocks,
please [install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).

Our infrastructure is built using AWS, so you'll need an AWS account, and access to the cli to run the project. You will
need to create a named profile (We suggest 'gov').

Follow these steps to set up the AWS profile:

- [Install/Update AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Set up a named profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) if you already
  have the AWS cli.

After setting up the named profile, the current session can be checked by running ```aws sts get-caller-identity```. We
have a [file](scripts/env_setup.sh)
with the required exports to use the 'gov' profile. These exports have to be run when starting a new session.

We use `jq` in our scripts to help the `make` targets work correctly,
please [Install jq](https://stedolan.github.io/jq/download/) before running any make command.

### Infrastructure Configuration

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
├── rapid-infrastructure
│   ├── blocks
│   ├── modules
│   └── etc...
├── rapid-infrastructure-config
│   ├── input-params.tfvars
│   └── backend.hcl
```

If you wish to use a different location, then please run:

```
export RAPID_INFRA_CONFIG_ENV=../my/relative/location/to/rapid/infrastructure
```

If you want to share your infrastructure values across your team then you can turn `rapid-infrastructure-config` into a private repo.

### First time, one-off setup (backend)

The first step is to set up an S3 backend so that we can store the infra-blocks' state in S3 and rely on the DynamoDB lock
mechanism to ensure infrastructure changes are applied atomically.

To set up the S3 backend follow these steps:

- Replace the values in `backend.hcl` with your custom values (these can be any value you would like). They will be referenced to create the Terraform state components and used going forwards as the backend config.
- In the root folder run ```make backend```, this will initialise Terraform by creating both the state bucket and dynamodb table in AWS.

### IAM User Setup (Optional)

This module is used to set the admin and user roles for the AWS account. It ensures a good level of security by expiring credentials quickly and ensuring that MFA is always needed to refresh them.

> ⚠️ CAUTION: If you have existing AWS users and don't include them as part of the manual_users, this block will remove them!

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

#### Assume role

In order to gain the admin privileges necessary for infrastructure changes one needs to assume admin role. This will be
enabled only for user's defined in `input-params.tfvars`, only after logging into the AWS console for the first time as an
IAM user and enabling MFA.

Then, to assume the role, set up the [profile](scripts/env_setup.sh), run ```make assume-role``` and follow the prompts.

### Deploying remaining infra-blocks

Once the state backend has been configured, provide/change the following inputs in `input-params.tfvars`.

Required:

- `state_bucket` - The name of the state bucket, as defined in `backend.hcl`
- `data_bucket_name` - This will be the bucket where the data is going to be stored, it needs to be a unique name.
- `log_bucket_name` - This is the bucket that will be used for logging, it needs to have a unique name.
- `iam_account_alias` - account alias required by AWS, it needs to be a unique name
- `application_version` - service's docker
  image [version](https://github.com/no10ds/rapid-api/blob/master/changelog.md)
- `ui_version` - Static UI [version](https://github.com/no10ds/rapid-ui/blob/master/CHANGELOG.md)
- `domain_name` - application hostname ([can be a domain or a subdomain](#managing-domainssubdomains))
- `aws_account` - aws account id where the application will be hosted
- `aws_region` - aws region where the application will be hosted
- `iam_users` - IAM users to be created automatically, with roles to be attached to them
- `manual_users` - IAM users that has been already created manually, with roles to be attached. (Can be left empty)
- `set_iam_user_groups` - User groups that need to be present on each user. (i.e. if the value is set to admin, then all
  the users will require the admin role)
- `support_emails_for_cloudwatch_alerts` - list of engineer emails that should receive alert notifications [more info](#alerting-and-monitoring)
- `ip_whitelist` - ip range to add to application whitelist. The expected value is a list of strings.

Optional:

- `resource-name-prefix` - prefix value for resource names, can be left as rapid
- `hosted_zone_id` - if provided, will add an alias for the application load balancer to use the provided domain using
  that HZ. Otherwise, it will create a HZ and the alias
- `certificate_validation_arn` - if provided, will link the certificate to the load-balancer https-listener. Otherwise,
  will create a new certificate and link it. ([managing certificates](#managing-certificates)
- `tags` - if provided, it will tag the resources with the defined value. Otherwise, it will default to "Resource = '
  data-f1-rapid'"

Then, run the following command on each block:

- ```make init block=<block-name>``` to initialise Terraform
- ```make plan block=<block-name>``` to plan (to check the changes ensuring nothing will be run)
- ```make apply block=<block-name>``` to apply changes, when prompted type ```yes```

Run the blocks in this order:

1. [iam-config](#iam-user-setup-optional) (optional) ⚠️ All the users' roles/policies will be handled here and will
delete any previous config ⚠️
2. vpc
3. s3
4. auth
5. data-workflow
6. app-cluster
7. ui

### Applying changes

For this we use make - some commands require the infrastructure block to be specified (see above):

```
>>> `make`
help:                    List targets and description
(...)

assume-role:       assume role to perform infrastructure tasks
init:              terraform init: make init block=<block>
precommit:         tf format and validate: make precommit block=<infra-block>
precommit-all:     .... for all the infrastructure blocks
plan:              plan - view infrastructure changes: make plan block=<infra-block>
apply:             apply infrastructure changes: make apply block=<infra-block>
output:         prints infrastructure output: make output block=<infra-block>

(...)
```

If you need to run manual Terraform commands for debugging or destroying you can set the necessarily variables like so:

```
>>> . ./scripts/env_setup.sh

```

### Building blocks

After the backend has been created the building blocks are:

- [app-cluster](blocks/app-cluster):
  - LB resources setup
  - domain/routing setup
  - ecs setup
  - firewall rules setup
  - access setup/management for the app to aws resources
  - DynamoDB setup
- [auth](blocks/auth):
  - cognito user pool setup
  - resource server setup
  - client app setup
  - DynamoDB setup
- [data-workflow](blocks/data-workflow):
  - athena setup
  - crawlers setup
  - glue resources setup
- [iam-config](blocks/iam-config):
  - iam users setup
  - iam roles/resources setup
  - config and infrastructure checks (avoid common pitfalls)
- [s3](blocks/s3):
  - data storage setup
- [vpc](blocks/vpc):
  - vpc setup
  - public/private subnets setup
- [ui](blocks/ui):
  - public S3 bucket
  - download & upload static html files
  - create cloudfront cdn

More formally the infrastructure blocks have been organised bearing in mind the cadence of change. They are organised in
separate folders so that they each have their own remote Terraform state file:

```
├── blocks
│   ├── auth
│   ├── app-cluster
│   ├── data-workflow
│   ├── ecr
│   ├── iam-config
│   ├── pipeline
│   ├── s3
│   ├── vpc
│   └── ui
```

## Managing domains/subdomains

When creating a rAPId instance you will need a hostname to be able to access the app in a secure way, there are few ways
to achieve this:

1. Using an existing domain from route53: AWS creates a hosted zone linked to your domain, just use this HZ id in the
inputs along the domain, and you are ready to go. (If the domain is currently being used, a subdomain can be created
automatically by providing the HZ id and the subdomain name in the `input-params.tfvars`).

2. Creating a new domain in route53: you will need to manually register a domain in the AWS console, once this is done
the steps are the same as scenario 1.

3. Using an existing domain outside AWS: you will need to leave the HZ id field empty and provide a
domain/subdomain, [copy the NS values from the output](#providing-outputs) and use them in your DNS provider.

4. Using an existing domain from a different AWS account to create a subdomain: you will need to leave the HZ id field
empty and provide the subdomain name, then [copy the NS values from the output](#providing-outputs), go to the AWS
account that owns the domain, go to route 53, in the domain hosted zone, create a new record of the type NS with the
subdomain name and add the NS values copied from the outputs.

## Managing certificates

When creating a rAPId instance a certificate will be needed in order to serve the application in HTTPS, there are 2
scenarios:

1. The AWS account already has a certificate for the domain you are using (this might be true for the first and second
scenario when [managing domains/subdomains](#managing-domainssubdomains)), in which case you can provide the certificate
arn for it to be used in the load balancer in the `input-params.tfvars`).

2. The AWS account does not have a certificate for the domain you plan to use, (this might be true for the third and
fourth scenario when [managing domains/subdomains](#managing-domainssubdomains)), in which case you need to leave the
certificate information empty in the `input-params.tfvars`)
. [AWS can not use the certificate from a different account](https://aws.amazon.com/premiumsupport/knowledge-center/acm-export-certificate/#:~:text=You%20can't%20export%20an,AWS%20Region%20and%20AWS%20account.)
, and therefore you will be required to create a new one (this will be handled automatically).

## Providing outputs

If you are planning to use a subdomain, and the domain is being handled in a different place you will need the name
server information. If the Hosted Zone was created by Terraform, you can get the NS information
running ```make output block=app-cluster``` under the name 'hosted_zone_name_servers'

## Pipeline and ECR Provisioning

⚠️ The `pipeline` and `ecr` Terraform blocks are only here for the rAPId application development team ⚠️

## Alerting and Monitoring

The rAPId service comes with pre-configured alerts that are triggered when a log with level `ERROR` is produced by the
application. In order to notify engineers of this type of alert, the parameter `support_emails_for_cloudwatch_alerts`
must be defined with a list of emails that should receive alert notifications.

```
module "app_cluster" {
  source = "git::https://github.com/no10ds/rapid-infrastructure//modules//app-cluster"

  ...

  support_emails_for_cloudwatch_alerts = ["someone@email.com", "support@email.com"]

  ...
}
```

> ⚠️ Make sure to **confirm** the notification subscription email in order to start receiving alert emails.

### ️ M1 Chip Issues

If you are running the M1 laptop you may have an issue with running Terraform init with providers and dependencies not
being found.

#### To install the AWS provider (v3.65.0) from source, run

Please note a prerequisite to setting up the AWS provider is installing go. You can use the following command:
`brew install go`

```
git clone https://github.com/hashicorp/terraform-provider-aws.git
cd terraform-provider-aws
git checkout v3.65.0
cd tools
go get -d github.com/pavius/impi/cmd/impi
cd ..
make tools
make build
```

Then copy the built binary (`terraform-provider-aws`) from `$GOPATH/bin/` to:

`~/.terraform.d/plugins/registry.terraform.io/hashicorp/aws/3.65.0/darwin_arm64/`
If for some reason your go path is not set it is most likely in `~/go`

#### To install the AWS provider template (v2.2.0) from source, run

```
git clone git@github.com:hashicorp/terraform-provider-template.git
cd terraform-provider-template
make build
```

Then copy the built binary (`terraform-provider-template`) from `$GOPATH/bin/` to:

`~/.terraform.d/plugins/registry.terraform.io/hashicorp/template/2.2.0/darwin_arm64`
If for some reason your go path is not set it is most likely in `~/go`

After running all the modules with the required information, you will need
to [provide some Terraform outputs](#providing-outputs) to the rAPId team.
