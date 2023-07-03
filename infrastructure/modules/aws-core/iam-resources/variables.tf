variable "iam_account_alias" {
  type        = string
  description = "A globally unique identifier, human-readable for your AWS account"
}

variable "users_account_id" {
  type        = string
  description = "The account ID of where the users are living in"
  default     = ""
}

variable "set_iam_account_alias" {
  type        = bool
  description = "Whether or not to set the account alias (useful to set to false when iam-users and iam-resources module are being deployed into the same account)"
  default     = true
}

variable "admin_multi_factor_auth_age" {
  type        = string
  description = "The amount of time (in seconds) for a admin session to be valid"
  default     = "3600"
}

variable "user_multi_factor_auth_age" {
  type        = string
  description = "The amount of time (in seconds) for a user session to be valid"
  default     = "14400"
}

variable "admin_access_role_name" {
  type        = string
  description = "Name of the admin role"
  default     = "resource-admin"
}

variable "user_access_role_name" {
  type        = string
  description = "Name of the user role"
  default     = "resource-user"
}

variable "admin_max_session_duration" {
  type        = string
  description = "The maximum session duration for the admin role"
  default     = "3600"
}

data "aws_caller_identity" "current" {}

locals {
  administrator_access_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  iam_read_only_access_policy_arn = "arn:aws:iam::aws:policy/IAMReadOnlyAccess"
  power_user_access_policy_arn    = "arn:aws:iam::aws:policy/PowerUserAccess"
  users_account_id                = length(var.users_account_id) > 0 ? var.users_account_id : data.aws_caller_identity.current.account_id
}
