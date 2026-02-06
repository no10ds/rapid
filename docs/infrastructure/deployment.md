# Deployment

## rAPId Module

For departments that already have an existing infrastructure, we have extracted the top level infrastructure into a single Terraform [module](https://github.com/no10ds/rapid/tree/main/infrastructure/modules/rapid).

### Usage

```
module "rapid" {
  source  = "git@github.com:no10ds/rapid.git//infrastructure/modules/rapid"

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
- `domain_name` - Application hostname ([can be a domain or a subdomain](./domains_subdomains.md))
- `ip_whitelist` - A list of IP addresses that are allowed to access the service.
- `public_subnet_ids_list` - List of public subnets for the load balancer
- `private_subnet_ids_list` - List of private subnets for the ECS service
- `vpc_id` - VPC id
- `resource-name-prefix` - The prefix that will be given to all of these rAPId resources, it needs to be unique so to not conflict with any other instance e.g `rapid-<your-team/project/dept>`
- `support_emails_for_cloudwatch_alerts` - List of engineer emails that should receive alert notifications

There are also these optional inputs:

- `application_version` - The service's image version
- `ui_version` - The version of the static frontend site
- `hosted_zone_id` - If provided, will add an alias for the application load balancer to use the provided domain using that HZ. Otherwise, it will create a HZ and the alias
- `certificate_validation_arn` - If provided, will link the certificate to the load-balancer https-listener. Otherwise, will create a new certificate and link it. ([managing certificates](./certificates.md))
- `app-replica-count-desired` - if provided, will set the number of desired running instances for a service. Otherwise,
  it will default the count to 1
- `app-replica-count-max` - if provided, will set the number of maximum running instances for a service. Otherwise, it
  will default the count to 2
- `catalog_disabled` - if set to `true` it will disable the rAPId internal data catalogue
- `tags` - if provided, it will tag the resources with the defined value. Otherwise, it will default to "Resource = '
  data-f1-rapid'"
- `custom_user_name_regex` - Regex that when supplied usernames must conform to when creating a new user. Defaults to none, in which case rAPId will default to it's basic username validity checks.
- `task_cpu` - If provided, will update CPU resource allocated to the ECS task running rAPId instance. Otherwise will default to 256.
- `task_memory` - If provided, will update memory resource allocated to the ECS task running rAPId instance. Otherwise will default to 512.

Once you apply the Terraform, a new instance of the application should be created.

## rAPId Full Stack

For teams with no existing infrastructure and just a blank AWS Account, we have `make` commands that will set up the necessary infrastructure from scratch with sensible defaults.

### Pre-requisites

Most of the infrastructure is managed by Terraform, to be able to run these blocks, please [install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).

Our infrastructure is built using AWS, so you'll need an AWS account, and access to the cli to run the project. You will need to create a named profile (We suggest 'gov').

Follow these steps to set up the AWS profile:

- [Install/Update AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

We use `jq` in our scripts to help the `make` targets work correctly, please [Install jq](https://stedolan.github.io/jq/download/) before running any make command.

### Infrastructure Configuration

There are two config files needed to instantiate the rAPId service, they are `input-params.tfvars` and `backend.hcl`. Please create these with the templates provided, we will add the content shortly.

`input-params.tfvars` template:

```
state_bucket = ""
data_bucket_name = ""
log_bucket_name = ""

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
task_memory = ""
task_cpu = ""
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

### First time, one-off setup (backend)

The first step is to set up an S3 backend so that we can store the infra-blocks' state in S3 and rely on the DynamoDB lock
mechanism to ensure infrastructure changes are applied atomically.

To set up the S3 backend follow these steps:

- Replace the values in `backend.hcl` with your custom values (these can be any value you would like). They will be referenced to create the Terraform state components and used going forwards as the backend config.
- In the root folder run `make infra/backend`, this will initialise Terraform by creating both the state bucket and dynamodb table in AWS.

### Deploying infra-blocks

Once the state backend has been configured, provide/change the following inputs in `input-params.tfvars`.

Required:

- `state_bucket` - The name of the state bucket, as defined in `backend.hcl`
- `data_bucket_name` - This will be the bucket where the data is going to be stored, it needs to be a unique name.
- `log_bucket_name` - This is the bucket that will be used for logging, it needs to have a unique name.
- `application_version` - service's docker
  image version
- `ui_version` - The version of the static frontend site
- `domain_name` - application hostname ([can be a domain or a subdomain](./domains_subdomains.md))
- `aws_account` - aws account id where the application will be hosted
- `aws_region` - aws region where the application will be hosted
- `support_emails_for_cloudwatch_alerts` - list of engineer emails that should receive alert notifications [more info](./alerting_monitoring.md)
- `ip_whitelist` - ip range to add to application whitelist. The expected value is a list of strings.

Optional:

- `resource-name-prefix` - prefix value for resource names, can be left as rapid
- `hosted_zone_id` - if provided, will add an alias for the application load balancer to use the provided domain using
  that HZ. Otherwise, it will create a HZ and the alias
- `certificate_validation_arn` - if provided, will link the certificate to the load-balancer https-listener. Otherwise,
  will create a new certificate and link it. [managing certificates](./certificates.md)
- `tags` - if provided, it will tag the resources with the defined value. Otherwise, it will default to "Resource = '
  data-f1-rapid'"

Then, run the following command on each block:

- `make infra/init block=<block-name>` to initialise Terraform
- `make infra/plan block=<block-name>` to plan (to check the changes ensuring nothing will be run)
- `make infra/apply block=<block-name>` to apply changes, when prompted type `yes`

Run the blocks in this order:

1. vpc
2. s3
3. auth
4. data-workflow
5. app-cluster
6. ui
