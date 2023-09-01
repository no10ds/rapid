data "terraform_remote_state" "vpc-state" {
  backend   = "s3"
  workspace = "prod"

  config = {
    key    = "vpc/terraform.tfstate"
    bucket = var.state_bucket
  }
}
