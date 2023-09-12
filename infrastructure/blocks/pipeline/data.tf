data "terraform_remote_state" "vpc-state" {
  backend   = "s3"
  workspace = "prod"

  config = {
    key    = "vpc/terraform.tfstate"
    bucket = var.state_bucket
  }
}


data "terraform_remote_state" "s3-state" {
  backend   = "s3"
  workspace = "prod"

  config = {
    key    = "s3/terraform.tfstate"
    bucket = var.state_bucket
  }
}

data "terraform_remote_state" "s3-state-preprod" {
  backend   = "s3"
  workspace = "preprod"

  config = {
    key    = "s3/terraform.tfstate"
    bucket = var.state_bucket
  }
}

data "terraform_remote_state" "s3-state-dev" {
  backend   = "s3"
  workspace = "dev"

  config = {
    key    = "s3/terraform.tfstate"
    bucket = var.state_bucket
  }
}

data "terraform_remote_state" "ecr-state" {
  backend = "s3"

  config = {
    key    = "ecr/terraform.tfstate"
    bucket = var.state_bucket
  }
}

data "aws_ami" "this" {
  most_recent = true
  name_regex  = "pipeline-ami-${var.pipeline_ami_version}"
  owners      = ["self"]
}
