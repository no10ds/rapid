variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
}

variable "state_bucket" {
  type        = string
  description = "Bucket name for backend state"
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the rAPId service"
}
