For departments that already have an existing infrastructure, we have extracted the top level infrastructure into a single Terraform [module](https://github.com/no10ds/rapid/tree/main/infrastructure/modules/rapid).

## Usage

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
- `domain_name` - Application hostname ([can be a domain or a subdomain](/infrastructure/domains_subdomains/))
- `ip_whitelist` - A list of IP addresses that are allowed to access the service.
- `public_subnet_ids_list` - List of public subnets for the load balancer
- `private_subnet_ids_list` - List of private subnets for the ECS service
- `vpc_id` - VPC id
- `resource-name-prefix` - The prefix that will be given to all of these rAPId resources, it needs to be unique so to not conflict with any other instance e.g `rapid-<your-team/project/dept>`
- `support_emails_for_cloudwatch_alerts` - List of engineer emails that should receive alert notifications

There are also these optional inputs:

- `application_version` - The service's image version
- `ui_version` - The static UI version
- `hosted_zone_id` - If provided, will add an alias for the application load balancer to use the provided domain using that HZ. Otherwise, it will create a HZ and the alias
- `certificate_validation_arn` - If provided, will link the certificate to the load-balancer https-listener. Otherwise, will create a new certificate and link it. ([managing certificates](/infrastructure/certificates/))
- `app-replica-count-desired` - if provided, will set the number of desired running instances for a service. Otherwise,
  it will default the count to 1
- `app-replica-count-max` - if provided, will set the number of maximum running instances for a service. Otherwise, it
  will default the count to 2
- `catalog_disabled` - if set to `true` it will disable the rAPId internal data catalogue
- `tags` - if provided, it will tag the resources with the defined value. Otherwise, it will default to "Resource = '
  data-f1-rapid'"

Once you apply the Terraform, a new instance of the application should be created.
