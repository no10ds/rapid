variable "bucket_prefix" {
  type        = string
  description = "The prefix attached to the AWS Config S3 bucket where evaluation results are stored"
  # The module default is "aws-config" so you don't necessarily need to specify this
  default = "rapid-aws-config-bucket"
}

variable "iam_account_alias" {
  type        = string
  description = "Unique alias name for the iam account"
}

variable "enable_lifecycle_management_for_s3" {
  type        = bool
  description = "Whether or not to enable lifecycle management for the created S3 buckets"
  # You should set this to true, or just delete the line (the default is "true"), if you're moving this into a production context
  default = true
}

variable "set_iam_user_groups" {
  type        = list(string)
  description = "A list of user groups every user should belong to"
}

variable "iam_users" {
  type        = map(map(list(string)))
  description = "A list of users you want to create inside the \"users\" account"
}

variable "manual_users" {
  type        = map(map(list(string)))
  description = "A list of users that were created manually into the account"
}

variable "password_policy" {
  type = object({
    require_uppercase_characters   = bool
    require_lowercase_characters   = bool
    require_symbols                = bool
    require_numbers                = bool
    minimum_password_length        = number
    password_reuse_prevention      = number
    max_password_age               = number
    allow_users_to_change_password = bool
  })
  description = "The password policy for the IAM users"
}
