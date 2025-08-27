terraform {
  backend "s3" {
    key = "ses/terraform.tfstate"
  }
}

module "ses" {
  source = "../../modules/ses"

  ses_service                              = var.ses_service
  resource-name-prefix                     = var.resource-name-prefix
  aws_account                              = var.aws_account
  aws_region                               = var.aws_region
  tags                                     = var.tags
  domain_name                              = var.domain_name
  hosted_zone_id                           = var.hosted_zone_id
  ses_support_emails_for_cloudwatch_alerts = var.ses_support_emails_for_cloudwatch_alerts
  allowed_sender_email_addresses           = var.allowed_sender_email_addresses
  allowed_recipients_email_domains         = var.allowed_recipients_email_domains
}
