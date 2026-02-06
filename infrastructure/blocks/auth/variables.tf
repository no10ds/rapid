variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
}

variable "domain_name" {
  type        = string
  description = "Domain name for the rAPId instance"
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}

variable "layers" {
  type        = list(string)
  description = "A list of the layers that the rAPId instance will contain"
  default     = ["default"]
}