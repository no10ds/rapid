variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
  default     = {}
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}
