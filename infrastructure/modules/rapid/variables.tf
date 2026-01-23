variable "app-replica-count-desired" {
  type        = number
  description = "The desired number of replicas of the app"
  default     = 1
}

variable "app-replica-count-max" {
  type        = number
  description = "The maximum desired number of replicas of the app"
  default     = 2
}

variable "application_version" {
  type        = string
  description = "The version number for the application image (e.g.: v1.0.4, v1.0.x-latest, etc.)"
  default     = "v7.15.1"
}

variable "ui_version" {
  type        = string
  description = "The version number for the static ui (e.g.: v1.0.0, etc.)"
  default     = "v7.15.1"
}

variable "catalog_disabled" {
  type        = bool
  description = "Optional value on whether to disable the internal rAPId data catalog"
  default     = false
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the rAPId service"
}

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the rAPId service"
}

variable "certificate_validation_arn" {
  type        = string
  description = "Arn of the certificate used by the domain"
  default     = ""
}

variable "us_east_certificate_validation_arn" {
  type        = string
  description = "Arn of the certificate used by Cloudfront. Please note this has to live in us-east-1."
  default     = ""
}

variable "domain_name" {
  type        = string
  description = "Domain name for the rAPId instance"
}

variable "allowed_email_domains" {
  type        = string
  description = "List of allowed emails domains that can be associated with users"
}

variable "hosted_zone_id" {
  type        = string
  description = "Hosted Zone ID with the domain Name Servers, pass quotes to create a new one from scratch"
  default     = ""
}

variable "ip_whitelist" {
  type        = list(string)
  description = "A list of IPs to whitelist for access to the service"
}

variable "enable_cloudtrail" {
  type        = bool
  description = "Whether to enable the logging of db events to CloudTrail"
  default     = true
}

variable "geo_restriction_locations" {
  description = "The ISO 3166-1-alpha-2 codes for which you want CloudFront either to distribute your content (whitelist)."
  type        = list(string)
  default     = ["GB"]
}

variable "sql_injection_protection" {
  description = "Whether to add SQL injection protection rule to WAF. Setting the variable to false may result in reduced application protection."
  type        = bool
  default     = true
}

variable "password_policy" {
  type = object({
    minimum_length                   = number
    require_lowercase                = bool
    require_numbers                  = bool
    require_symbols                  = bool
    require_uppercase                = bool
    temporary_password_validity_days = number
  })
  description = "The Cognito pool password policy"
  default = {
    minimum_length                   = 10
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }
}

variable "cognito_ses_authentication" {
  type        = bool
  description = "Configure Cognito user pool to send emails with SES instead of SNS. If you choose SNS make sure you moved it from sandbox to production environment."
  default     = false
}

variable "ses_domain_identity_arn" {
  type        = string
  description = "The ARN of the SES domain identity to use for Cognito email sending"
  default     = ""
} 

variable "ses_email_notifications" {
  type        = list(string)
  description = "List of email addresses that will receive SES notifications when an email results in a bounce or complaint response from the server"
  default     = null
}

variable "ses_allowed_from_emails" {
  type        = list(string)
  description = "List of email domains that SES can use to issue emails in AWS account"
  default     = null
}

variable "public_subnet_ids_list" {
  type        = list(string)
  description = "A list of public subnets from the VPC config"
}

variable "private_subnet_ids_list" {
  type        = list(string)
  description = "A list of private subnets from each organisation network config"
}

variable "rapid_ecr_url" {
  type        = string
  description = "ECR Url for task definition"
  default     = "public.ecr.aws/no10-rapid/api"
}

variable "resource-name-prefix" {
  type        = string
  description = "organization prefix of for naming"
}

variable "support_emails_for_cloudwatch_alerts" {
  type        = list(string)
  description = "List of emails that will receive alerts from CloudWatch"
}

variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
  default = {
    Resource = "data-f1-rapid"
  }
}

variable "vpc_id" {
  type        = string
  description = "The ID of the multihost VPC"
}

variable "ecs_cluster_id" {
  type        = string
  default     = null
  description = "ECS cluster id to attach the rAPId api to"
}

variable "ecs_cluster_arn" {
  type        = string
  default     = null
  description = "ECS cliuster arn to attach the rAPId api to"
}

variable "ecs_cluster_name" {
  type        = string
  default     = null
  description = "ECS cluster name to attach the rAPId api to"
}

variable "layers" {
  type        = list(string)
  description = "A list of the layers that the rAPId instance will contain"
  default     = ["default"]
}

variable "custom_user_name_regex" {
  type        = string
  description = "A regex expression for conditional user validation."
  default     = null
  nullable    = true
}

variable "task_memory" {
  type        = number
  description = "rAPId ecs task memory"
  default     = 512
}

variable "task_cpu" {
  type        = number
  description = "rAPId ecs task cpu"
  default     = 256
}
