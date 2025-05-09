variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
}

variable "domain_name" {
  type        = string
  description = "Domain name for the rAPId instance"
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the rAPId service"
}

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the rAPId service"
}

variable "allowed_email_domains" {
  type        = string
  description = "List of allowed emails domains that can be associated with users"
}

variable "cognito_ses_authentication" {
  type        = bool
  description = "Whether to use SES instead of SNS for authentication. If you choose SNS make sure you moved it from sandbox to production environment."
}

variable "ses_allowed_from_emails" {
  type        = list(string)
  description = "List of email domains that SES can use to issue emails in AWS account"
}

variable "hosted_zone_id" {
  type        = string
  description = "The hosted zone ID for the domain name"
}

variable "ses_email_notifications" {
  type        = list(string)
  description = "List of email addresses that will receive SES notifications when an email results in a bounce or complaint response from the server"

}
