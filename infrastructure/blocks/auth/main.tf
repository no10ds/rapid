terraform {
  backend "s3" {
    key = "auth/terraform.tfstate"
  }
}

module "auth" {
  source = "../../modules/auth"

  tags                       = var.tags
  domain_name                = var.domain_name
  resource-name-prefix       = var.resource-name-prefix
  aws_region                 = var.aws_region
  allowed_email_domains      = var.allowed_email_domains
  aws_account                = var.aws_account
  cognito_ses_authentication = var.cognito_ses_authentication
  ses_allowed_from_emails    = var.ses_allowed_from_emails
  hosted_zone_id             = var.hosted_zone_id
  ses_email_notifications    = var.ses_email_notifications
}
