terraform {
  backend "s3" {
    key = "pipeline/terraform.tfstate"
  }
}
