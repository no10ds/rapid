terraform {
  backend "s3" {
    key = "vpc/terraform.tfstate"
  }
}


data "aws_availability_zones" "available" {}


module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"

  name                 = "${var.resource-name-prefix}_vpc"
  cidr                 = "10.0.0.0/16"
  azs                  = data.aws_availability_zones.available.names
  private_subnets      = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets       = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
  enable_nat_gateway   = true
  enable_dns_hostnames = true

  default_network_acl_ingress = [
    { rule_no = 100, action = "allow", protocol = "tcp", from_port = 80, to_port = 80, cidr_block = "0.0.0.0/0" },
    { rule_no = 110, action = "allow", protocol = "tcp", from_port = 443, to_port = 443, cidr_block = "0.0.0.0/0" },
    # Return traffic for outbound connections (via NAT gateway)
    { rule_no = 120, action = "allow", protocol = "tcp", from_port = 1024, to_port = 65535, cidr_block = "0.0.0.0/0" },
    { rule_no = 130, action = "allow", protocol = "-1", from_port = 0, to_port = 0, cidr_block = "10.0.0.0/16" },
  ]

  default_network_acl_egress = [
    { rule_no = 100, action = "allow", protocol = "-1", from_port = 0, to_port = 0, cidr_block = "0.0.0.0/0" },
  ]
}
