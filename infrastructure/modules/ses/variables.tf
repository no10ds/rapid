variable "ses_service" {
  type        = bool
  description = "Whether to create SES service for given hosted zone"
}

variable "resource-name-prefix" {
  type        = string
  description = "organization prefix of for naming"
}

variable "tags" {
  type        = map(string)
  description = "A common map of tags for all resources that are created (for e.g. billing purposes)"
  default     = {}
}

variable "domain_name" {
  type        = string
  description = "Domain name for the rAPId instance"
}

variable "hosted_zone_id" {
  type        = string
  description = "Hosted Zone ID used for rAPId domain name"
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the rAPId service"
}

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the rAPId service"
}

variable "ses_support_emails_for_cloudwatch_alerts" {
  type        = list(string)
  description = "List of email addresses that will receive SES notifications when an email results in a bounce or complaint response from the server"
  default     = null
  validation {
    condition     = var.ses_service == false || try(length(var.ses_support_emails_for_cloudwatch_alerts), 0) > 0
    error_message = "SES requires at least one email address for SES notifications"
  }
}

variable "allowed_sender_email_addresses" {
  type        = list(string)
  description = "List of email addresses that SES can use to send emails. no-reply@domainname address is enabled by default"
}

variable "allowed_recipients_email_domains" {
  type        = string
  description = "List of allowed recipients email domains that SES service is allowed to send emails to. simulator.amazonses.com is enabled by default"
}
