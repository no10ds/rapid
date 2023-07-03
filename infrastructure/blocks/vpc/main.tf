terraform {
  backend "s3" {
    key = "vpc/terraform.tfstate"
  }
}

module "core_vpc" {
  source = "../../modules/aws-core/vpc"

  tags           = var.tags
  vpc_name       = "${var.resource-name-prefix}_vpc"
  vpc_cidr_range = "10.1.0.0/16"

  private_subnet_size = 6
  /* the minimum subnet size in aws is /28 https://aws.amazon.com/vpc/faqs/ */
  private_subnet_cidrs  = ["10.1.10.0/28", "10.1.11.0/28", "10.1.12.0/28", "10.1.13.0/28", "10.1.14.0/28", "10.1.15.0/28"]
  private_subnet_offset = 2
  private_subnet_prefix = "${var.resource-name-prefix}_private_"

  public_subnet_size   = 3
  public_subnet_cidrs  = ["10.1.1.0/28", "10.1.2.0/28", "10.1.3.0/28"]
  public_subnet_prefix = "${var.resource-name-prefix}_public_"
}
