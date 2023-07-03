variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to all VPC resources"
  default     = {}
}

variable "vpc_name" {
  type        = string
  description = "The name of the VPC"
  default     = "core_vpc"
}

variable "vpc_cidr_range" {
  type        = string
  description = "The IP address space to use for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "A list of CIDRs for the public subnets. Needs to be the same amount as subnets in the Availability Zone you are deploying into (probably 3)"
  default     = []
}

variable "public_subnet_size" {
  type        = number
  description = "The size of the public subnet (default: 1022 usable addresses)"
  default     = "6"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "A list of CIDRs for the private subnets. Needs to be the same amount as subnets in the Availability Zone you are deploying into (probably 3)"
  default     = []
}

variable "private_subnet_size" {
  type        = number
  description = "The size of the private subnet (default: 1022 usable addresses)"
  default     = 6
}

variable "private_subnet_offset" {
  type        = number
  description = "The amount of IP space between the public and the private subnet"
  default     = 32
}

variable "public_subnet_prefix" {
  type        = string
  description = "The prefix to attach to the name of the public subnets"
  default     = ""
}

variable "private_subnet_prefix" {
  type        = string
  description = "The prefix to attach to the name of the private subnets"
  default     = ""
}

variable "enable_dns_support" {
  type        = bool
  description = "Whether or not to enable VPC DNS support"
  default     = true
}

variable "enable_dns_hostnames" {
  type        = bool
  description = "Whether or not to enable VPC DNS hostname support"
  default     = true
}

locals {
  # We are using locals for this because there already is a fair amount of function calling inside the actual resources
  public_subnet_prefix  = length(var.public_subnet_prefix) > 0 ? var.public_subnet_prefix : "${var.vpc_name}_public_subnet"
  private_subnet_prefix = length(var.private_subnet_prefix) > 0 ? var.private_subnet_prefix : "${var.vpc_name}_private_subnet"
}

data "aws_availability_zones" "available" {}
