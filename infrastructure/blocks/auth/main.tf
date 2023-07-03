terraform {
  backend "s3" {
    key = "auth/terraform.tfstate"
  }
}

module "auth" {
  source = "../../modules/auth"

  tags                 = var.tags
  domain_name          = var.domain_name
  resource-name-prefix = var.resource-name-prefix
}
