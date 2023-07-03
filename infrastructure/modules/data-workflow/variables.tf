variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
  default = {
    Resource = "data-f1-rapid"
  }
}

variable "data_s3_bucket_arn" {
  type        = string
  description = "S3 Bucket arn to store application data"
}

variable "data_s3_bucket_name" {
  type        = string
  description = "S3 Bucket name to store application data"
}

variable "vpc_id" {
  type        = string
  description = "Application VPC"
}

variable "private_subnet" {
  type        = string
  description = "Application Private subnet"
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the rAPId service"
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the rAPId service"
}
