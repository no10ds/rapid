terraform {
  backend "s3" {
    key = "data-workflow/terraform.tfstate"
  }
}

module "data_workflow" {
  source = "../../modules/data-workflow"

  resource-name-prefix = var.resource-name-prefix
  aws_account          = var.aws_account
  aws_region           = var.aws_region
  data_s3_bucket_arn   = data.terraform_remote_state.s3-state.outputs.s3_bucket_arn
  data_s3_bucket_name  = data.terraform_remote_state.s3-state.outputs.s3_bucket_name
  vpc_id               = data.terraform_remote_state.vpc-state.outputs.vpc_id
  private_subnet       = data.terraform_remote_state.vpc-state.outputs.private_subnets_ids[0]
  tags                 = var.tags
}

data "terraform_remote_state" "vpc-state" {
  backend = "s3"

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
