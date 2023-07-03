terraform {
  backend "s3" {
    key = "ui/terraform.tfstate"
  }
}

module "ui" {
  source = "../../modules/ui"

  resource-name-prefix = var.resource-name-prefix

  load_balancer_dns = data.terraform_remote_state.app-cluster-state.outputs.load_balancer_dns

  ui_version                         = var.ui_version
  aws_account                        = var.aws_account
  log_bucket_name                    = var.log_bucket_name
  us_east_certificate_validation_arn = var.us_east_certificate_validation_arn
  domain_name                        = var.domain_name
  hosted_zone_id                     = var.hosted_zone_id != "" ? var.hosted_zone_id : data.terraform_remote_state.app-cluster-state.outputs.hosted_zone_id
  ip_whitelist                       = var.ip_whitelist
  tags                               = var.tags
}

data "terraform_remote_state" "app-cluster-state" {
  backend   = "s3"
  workspace = terraform.workspace
  config = {
    key    = "app-cluster/terraform.tfstate"
    bucket = var.state_bucket
  }
}

provider "aws" {
  alias  = "us_east"
  region = "us-east-1"

  default_tags {
    tags = var.tags
  }
}

resource "aws_cloudfront_origin_access_identity" "rapid_ui" {}
