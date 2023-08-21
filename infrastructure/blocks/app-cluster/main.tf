terraform {
  backend "s3" {
    key = "app-cluster/terraform.tfstate"
  }
}

module "app_cluster" {
  source = "../../modules/app-cluster"

  app-replica-count-desired = var.app-replica-count-desired
  app-replica-count-max     = var.app-replica-count-max
  resource-name-prefix      = var.resource-name-prefix

  cognito_user_pool_id                            = data.terraform_remote_state.auth-state.outputs.cognito_user_pool_id
  cognito_user_login_app_credentials_secrets_name = data.terraform_remote_state.auth-state.outputs.cognito_user_app_secret_manager_name
  permissions_table_arn                           = data.terraform_remote_state.auth-state.outputs.user_permission_table_arn
  schema_table_arn                                = data.terraform_remote_state.data-workflow-state.outputs.schema_table_arn

  application_version                  = var.application_version
  domain_name                          = var.domain_name
  allowed_email_domains                = var.allowed_email_domains
  aws_account                          = var.aws_account
  catalog_disabled                     = var.catalog_disabled
  aws_region                           = var.aws_region
  rapid_ecr_url                        = var.rapid_ecr_url
  hosted_zone_id                       = var.hosted_zone_id
  certificate_validation_arn           = var.certificate_validation_arn
  project_information                  = var.project_information
  data_s3_bucket_arn                   = data.terraform_remote_state.s3-state.outputs.s3_bucket_arn
  data_s3_bucket_name                  = data.terraform_remote_state.s3-state.outputs.s3_bucket_name
  log_bucket_name                      = data.terraform_remote_state.s3-state.outputs.log_bucket_name
  athena_query_output_bucket_arn       = data.terraform_remote_state.data-workflow-state.outputs.athena_query_output_bucket_arn
  vpc_id                               = data.terraform_remote_state.vpc-state.outputs.vpc_id
  private_subnet_ids_list              = data.terraform_remote_state.vpc-state.outputs.private_subnets_ids
  public_subnet_ids_list               = data.terraform_remote_state.vpc-state.outputs.public_subnets_ids
  ip_whitelist                         = var.ip_whitelist
  enable_cloudtrail                    = var.enable_cloudtrail
  support_emails_for_cloudwatch_alerts = var.support_emails_for_cloudwatch_alerts
  tags                                 = var.tags
}

data "terraform_remote_state" "vpc-state" {
  backend   = "s3"
  workspace = terraform.workspace
  config = {
    key    = "vpc/terraform.tfstate"
    bucket = var.state_bucket
  }
}

data "terraform_remote_state" "s3-state" {
  backend   = "s3"
  workspace = terraform.workspace
  config = {
    key    = "s3/terraform.tfstate"
    bucket = var.state_bucket
  }
}

data "terraform_remote_state" "data-workflow-state" {
  backend   = "s3"
  workspace = terraform.workspace
  config = {
    key    = "data-workflow/terraform.tfstate"
    bucket = var.state_bucket
  }
}

data "terraform_remote_state" "auth-state" {
  backend   = "s3"
  workspace = terraform.workspace
  config = {
    key    = "auth/terraform.tfstate"
    bucket = var.state_bucket
  }
}
