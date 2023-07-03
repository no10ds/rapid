terraform {
  backend "s3" {
    key = "iam-config/terraform.tfstate"
  }
}

module "config" {
  source = "../../modules/aws-core/config"

  bucket_prefix                      = var.bucket_prefix
  bucket_key_prefix                  = var.bucket_prefix
  enable_lifecycle_management_for_s3 = var.enable_lifecycle_management_for_s3
  password_policy                    = var.password_policy
}

module "iam_users" {
  source = "../../modules/aws-core/iam-users"

  # This includes some random bits here purely for demonstrational purposes. Please use a distinct unique identifier otherwise!
  iam_account_alias = var.iam_account_alias
  iam_users         = var.iam_users
  password_policy   = var.password_policy
}

module "iam_resources" {
  source = "../../modules/aws-core/iam-resources"

  # Mandatory parameter so we can't skip it
  iam_account_alias = var.iam_account_alias
  # This will make sure we're only setting the IAM account alias once, as we're operating in the same account
  set_iam_account_alias       = false
  admin_multi_factor_auth_age = "14400"
  admin_max_session_duration  = "14400"
}

resource "aws_iam_user_group_membership" "manual_user_memberships" {
  for_each = var.manual_users
  user     = each.key

  groups = each.value["groups"]
}
