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

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the rAPId service"
}

variable "version_check" {
  description = "Ensure that you have incremented the version of the ami. Enter 'yes' to continue"
  validation {
    condition     = var.version_check == "yes"
    error_message = "You must enter 'yes' to continue"
  }
}


variable "pipeline_ami_version" {
  type        = string
  description = "The version of the pipeline AMI to use"
}
