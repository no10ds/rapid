# This is a policy which lets you self-service your own access keys.
# The only condition is that you have a MFA enabled session
data "aws_iam_policy_document" "aws_access_key_self_service_policy" {
  statement {
    actions = [
      "iam:CreateAccessKey",
      "iam:DeleteAccessKey",
      "iam:ListAccessKeys",
      "iam:UpdateAccessKey",
    ]

    effect = "Allow"

    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["true"]
    }

    condition {
      test     = "NumericLessThan"
      variable = "aws:MultiFactorAuthAge"
      values   = [var.multi_factor_auth_age]
    }

    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/$${aws:username}",
    ]
  }
}

resource "aws_iam_policy" "aws_access_key_self_service" {
  name        = "aws_access_key_self_service"
  description = "Policy for access key self service"

  policy = data.aws_iam_policy_document.aws_access_key_self_service_policy.json
}

resource "aws_iam_account_password_policy" "strict" {
  # checkov:skip=CKV_AWS_11:Let users determine their own password policy
  # checkov:skip=CKV_AWS_12:Let users determine their own password policy
  # checkov:skip=CKV_AWS_13:Let users determine their own password policy
  # checkov:skip=CKV_AWS_14:Let users determine their own password policy
  # checkov:skip=CKV_AWS_15:Let users determine their own password policy
  minimum_password_length        = local.password_policy["minimum_password_length"]
  max_password_age               = local.password_policy["max_password_age"]
  password_reuse_prevention      = local.password_policy["password_reuse_prevention"]
  require_lowercase_characters   = local.password_policy["require_lowercase_characters"]
  require_numbers                = local.password_policy["require_numbers"]
  require_uppercase_characters   = local.password_policy["require_uppercase_characters"]
  require_symbols                = local.password_policy["require_symbols"]
  allow_users_to_change_password = local.password_policy["allow_users_to_change_password"]
}

# This allows users without MFA to at least get a few details about their own account
data "aws_iam_policy_document" "aws_list_iam_users_policy" {
  statement {
    effect = "Allow"

    actions = [
      "iam:GetAccountSummary",
      "iam:ListAccountAliases",
      "iam:ListGroupsForUser",
      "iam:ListUsers",
    ]

    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:*",
    ]
  }

  statement {
    actions = ["iam:GetUser"]

    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/$${aws:username}",
    ]

    effect = "Allow"
  }
}

resource "aws_iam_policy" "aws_list_iam_users" {
  name        = "aws_list_iam_users"
  description = "Let users see the list of users"

  policy = data.aws_iam_policy_document.aws_list_iam_users_policy.json
}

data "aws_iam_policy_document" "aws_mfa_self_service_policy" {
  statement {
    effect = "Allow"

    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/$${aws:username}",
    ]

    actions = [
      "iam:DeactivateMFADevice",
      "iam:EnableMFADevice",
      "iam:ResyncMFADevice",
      "iam:ListVirtualMFADevices",
      "iam:ListMFADevices",
    ]
  }

  statement {
    effect = "Allow"

    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:mfa/$${aws:username}",
    ]

    actions = [
      "iam:CreateVirtualMFADevice",
      "iam:DeleteVirtualMFADevice",
    ]
  }

  statement {
    effect = "Allow"

    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:mfa/*",
    ]

    actions = [
      "iam:ListVirtualMFADevices",
      "iam:ListMFADevices",
    ]
  }
}

resource "aws_iam_policy" "aws_mfa_self_service" {
  name        = "aws_mfa_self_service"
  description = "Policy for MFA self service"

  policy = data.aws_iam_policy_document.aws_mfa_self_service_policy.json
}

resource "aws_iam_account_alias" "iam_account_alias" {
  count         = var.set_iam_account_alias ? 1 : 0
  account_alias = var.iam_account_alias
}

# Users
resource "aws_iam_user" "users" {
  for_each = var.iam_users
  name     = each.key
}

resource "aws_iam_user_group_membership" "users_group_memberships" {
  depends_on = [
    aws_iam_user.users,
    aws_iam_group.groups
  ]
  for_each = var.iam_users
  user     = each.key

  groups = each.value["groups"]
}

# Groups
resource "aws_iam_group" "groups" {
  for_each = toset(concat(
    local.admin_groups,
    local.user_groups
  ))
  name = each.key
}

# Group policy assignments
resource "aws_iam_policy_attachment" "users_mfa_self_service" {
  name       = "users_mfa_self_service"
  groups     = values(aws_iam_group.groups)[*].name
  policy_arn = aws_iam_policy.aws_mfa_self_service.arn
}

resource "aws_iam_policy_attachment" "users_access_key_self_service" {
  name       = "users_access_key_self_service"
  groups     = values(aws_iam_group.groups)[*].name
  policy_arn = aws_iam_policy.aws_access_key_self_service.arn
}

resource "aws_iam_policy_attachment" "users_list_iam_users" {
  name       = "users_list_iam_users"
  groups     = values(aws_iam_group.groups)[*].name
  policy_arn = aws_iam_policy.aws_list_iam_users.arn
}

# Group policies
data "aws_iam_policy_document" "assume_role_admin_access_group_policy_document" {
  statement {
    actions = [
      "sts:AssumeRole",
    ]

    effect = "Allow"

    resources = [
      "arn:aws:iam::${local.resources_account_id}:role/${var.resource_admin_role_name}",
    ]
  }
}

resource "aws_iam_group_policy" "assume_role_admin_access_group_policy" {
  for_each = toset(local.admin_groups)
  name     = "admin_access_group_policy"
  group    = aws_iam_group.groups[each.key].id

  policy = data.aws_iam_policy_document.assume_role_admin_access_group_policy_document.json
}

data "aws_iam_policy_document" "assume_role_users_access_group_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    resources = [
      "arn:aws:iam::${local.resources_account_id}:role/${var.resource_user_role_name}"
    ]
  }
}

resource "aws_iam_group_policy" "assume_role_users_access_group_policy" {
  for_each = toset(local.user_groups)
  name     = "users_access_group_policy"
  group    = aws_iam_group.groups[each.key].id

  policy = data.aws_iam_policy_document.assume_role_users_access_group_policy_document.json
}
