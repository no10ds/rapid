terraform {
  backend "s3" {
    key = "pipeline-ami/terraform.tfstate"
  }
}
