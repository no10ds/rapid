variable "bucket_prefix" {
  type        = string
  description = "The prefix for the S3 bucket AWS Config Recorder writes to"
  default     = "aws-config"
}

variable "bucket_key_prefix" {
  type        = string
  description = "The prefix of the keys AWS Config writes to"
  default     = "aws_config"
}

variable "config_recorder_name" {
  type        = string
  description = "The name of the recorder for AWS Config"
  default     = "config"
}

variable "config_delivery_channel_name" {
  type        = string
  description = "The name of the delivery channel for AWS Config"
  default     = "config"
}

variable "iam_role_name" {
  type        = string
  description = "The name of the IAM role created for delegating permissions to AWS Config"
  default     = "config"
}

variable "bucket_account_id" {
  type        = string
  description = "The AWS account ID the S3 bucket lives in that AWS Config is writing its records to. Defaults to the ID of the current account"
  default     = ""
}

variable "delivery_frequency" {
  type        = string
  description = "The frequency at which AWS Config delivers its recorded findings to S3"
  default     = "Three_Hours"
}

variable "password_policy" {
  type        = map(string)
  description = "A map of values describing the password policy parameters AWS Config is looking for"
  default     = {}
}

variable "iam_user_groups" {
  type        = map(string)
  description = "A list of mandatory groups for IAM users"
  default     = {}
}

variable "max_access_key_age" {
  type        = string
  description = "The maximum amount of days an access key can live without being rotated"
  default     = "90"
}

variable "enable_lifecycle_management_for_s3" {
  type        = bool
  description = "Whether or not to enable lifecycle management for the S3 bucket AWS Config writes to"
  default     = true
}

variable "amis_by_tag_key_and_value_list" {
  type        = list(string)
  description = "Required AMI tags for EC2 instances"
  default     = []
}

variable "desired_instance_types" {
  type        = set(string)
  description = "A string of comma-delimited instance types"
  default     = []
}

variable "s3_kms_sse_encryption_key_arn" {
  type        = string
  description = "The ARN for the KMS key to use for S3 server-side bucket encryption"
  default     = "" # Use the default master key
}

locals {
  config_policy_arn = "arn:aws:iam::aws:policy/service-role/AWSConfigRole"
  bucket_account_id = length(var.bucket_account_id) > 0 ? var.bucket_account_id : data.aws_caller_identity.current.account_id
  password_policy = merge({
    require_uppercase_characters = true
    require_lowercase_characters = true
    require_symbols              = true
    require_numbers              = true
    minimum_password_length      = 32
    password_reuse_prevention    = 5
    max_password_age             = 90
  }, var.password_policy)
}

data "aws_caller_identity" "current" {}
