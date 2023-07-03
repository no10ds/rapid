terraform {
  backend "s3" {
    key = "pipeline/terraform.tfstate"
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

data "terraform_remote_state" "ecr-state" {
  backend = "s3"

  config = {
    key    = "ecr/terraform.tfstate"
    bucket = var.state_bucket
  }
}

resource "aws_instance" "pipeline" {
  #checkov:skip=CKV_AWS_135:EBS Optimised not available for instance type
  ami                         = "ami-00826bd51e68b1487"
  instance_type               = "t3.medium"
  associate_public_ip_address = false
  iam_instance_profile        = aws_iam_instance_profile.pipeline_instance_profile.name
  subnet_id                   = data.terraform_remote_state.vpc-state.outputs.private_subnets_ids[0]
  user_data                   = data.template_file.initialise-runner.rendered
  monitoring                  = true

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted   = true
    volume_size = 64
  }

  tags = merge(
    var.tags,
    {
      Name = "github-action-runner"
    },
  )
}

resource "aws_iam_instance_profile" "pipeline_instance_profile" {
  name = "pipeline_instance_profile"
  role = aws_iam_role.pipeline_ecr_role.name
}

data "template_file" "initialise-runner" {
  template = file("../../scripts/initialisation-script.sh.tpl")
  vars = {
    runner-registration-token = var.runner-registration-token
  }
}

data "terraform_remote_state" "vpc-state" {
  backend = "s3"

  config = {
    key    = "vpc/terraform.tfstate"
    bucket = var.state_bucket
  }
}
