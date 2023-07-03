variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
}

variable "runner-registration-token" {
  description = "The Github Actions Runner registration token (you can get this from Settings > Actions > Runner (or by hitting the relevant endpoint))"
  type        = string
}

variable "state_bucket" {
  type        = string
  description = "Bucket name for backend state"
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the rAPId service"
}

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the rAPId service"
}
