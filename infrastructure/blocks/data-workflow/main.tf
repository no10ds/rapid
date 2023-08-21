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
  tags                 = var.tags
}

data "terraform_remote_state" "s3-state" {
  backend   = "s3"
  workspace = terraform.workspace
  config = {
    key    = "s3/terraform.tfstate"
    bucket = var.state_bucket
  }
}
