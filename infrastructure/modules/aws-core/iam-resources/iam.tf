resource "aws_iam_account_alias" "iam_account_alias" {
  count         = var.set_iam_account_alias ? 1 : 0
  account_alias = var.iam_account_alias
}

# Roles
data "aws_iam_policy_document" "admin_access_role_policy" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["true"]
    }

    condition {
      test     = "NumericLessThan"
      variable = "aws:MultiFactorAuthAge"
      values   = [var.admin_multi_factor_auth_age]
    }

    principals {
      type = "AWS"

      identifiers = [
        "arn:aws:iam::${local.users_account_id}:root",
      ]
    }
  }
}

resource "aws_iam_role" "admin_access_role" {
  name                 = var.admin_access_role_name
  max_session_duration = var.admin_max_session_duration
  assume_role_policy   = data.aws_iam_policy_document.admin_access_role_policy.json
}

data "aws_iam_policy_document" "user_access_role_policy" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["true"]
    }

    condition {
      test     = "NumericLessThan"
      variable = "aws:MultiFactorAuthAge"
      values   = [var.user_multi_factor_auth_age]
    }

    principals {
      type = "AWS"

      identifiers = [
        "arn:aws:iam::${local.users_account_id}:root",
      ]
    }
  }
}

resource "aws_iam_role" "user_access_role" {
  name = var.user_access_role_name

  assume_role_policy = data.aws_iam_policy_document.user_access_role_policy.json
}

data "aws_iam_policy_document" "user_access_policy_document" {
  statement {
    effect = "Allow"

    actions = [
      "iam:PassRole",
    ]

    not_resources = [
      aws_iam_role.user_access_role.arn,
      aws_iam_role.admin_access_role.arn
    ]
  }
}

resource "aws_iam_policy" "user_access_policy" {
  name        = "user_access_policy"
  description = "User access for roles"

  policy = data.aws_iam_policy_document.user_access_policy_document.json
}

data "aws_iam_policy_document" "no_vpc_access_policy_document" {
  statement {
    effect = "Deny"

    actions = [
      "ec2:AcceptVpcPeeringConnection",
      "ec2:AssociateDhcpOptions",
      "ec2:AssociateRouteTable",
      "ec2:AttachClassicLinkVpc",
      "ec2:AttachInternetGateway",
      "ec2:AttachVpnGateway",
      "ec2:CreateCustomerGateway",
      "ec2:CreateDhcpOptions",
      "ec2:CreateFlowLogs",
      "ec2:CreateInternetGateway",
      "ec2:CreateNatGateway",
      "ec2:CreateNetworkAcl",
      "ec2:CreateNetworkAclEntry",
      "ec2:CreateRoute",
      "ec2:CreateRouteTable",
      "ec2:CreateSubnet",
      "ec2:CreateVpc",
      "ec2:CreateVpcPeeringConnection",
      "ec2:CreateVpnConnection",
      "ec2:CreateVpnConnectionRoute",
      "ec2:CreateVpnGateway",
      "ec2:DeleteCustomerGateway",
      "ec2:DeleteDhcpOptions",
      "ec2:DeleteInternetGateway",
      "ec2:DeleteNatGateway",
      "ec2:DeleteNetworkAcl",
      "ec2:DeleteNetworkAclEntry",
      "ec2:DeleteRoute",
      "ec2:DeleteRouteTable",
      "ec2:DeleteSubnet",
      "ec2:DeleteVpc",
      "ec2:DeleteVpnConnection",
      "ec2:DeleteVpnConnectionRoute",
      "ec2:DeleteVpnGateway",
      "ec2:DetachClassicLinkVpc",
      "ec2:DetachInternetGateway",
      "ec2:DetachVpnGateway",
      "ec2:DisableVgwRoutePropagation",
      "ec2:DisableVpcClassicLink",
      "ec2:DisableVpcClassicLinkDnsSupport",
      "ec2:DisassociateRouteTable",
      "ec2:EnableVgwRoutePropagation",
      "ec2:EnableVpcClassicLink",
      "ec2:EnableVpcClassicLinkDnsSupport",
      "ec2:ModifySubnetAttribute",
      "ec2:ModifyVpcAttribute",
      "ec2:ModifyVpcEndpoint",
      "ec2:ModifyVpcPeeringConnectionOptions",
      "ec2:MoveAddressToVpc",
      "ec2:RejectVpcPeeringConnection",
      "ec2:ReplaceNetworkAclAssociation",
      "ec2:ReplaceNetworkAclEntry",
      "ec2:ReplaceRoute",
      "ec2:ReplaceRouteTableAssociation",
      "ec2:RestoreAddressToClassic",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "user_no_vpc_access_policy" {
  name        = "user_no_vpc_access_policy"
  description = "deny user access to VPC related commands"

  policy = data.aws_iam_policy_document.no_vpc_access_policy_document.json
}

# Policy attachments for roles
resource "aws_iam_policy_attachment" "admin_access_policy_attachment" {
  name       = "admin_access_policy_attachment"
  roles      = [aws_iam_role.admin_access_role.name]
  policy_arn = local.administrator_access_policy_arn
}

resource "aws_iam_policy_attachment" "user_access_policy_attachment" {
  name       = "user_access_policy_attachment"
  roles      = [aws_iam_role.user_access_role.name]
  policy_arn = aws_iam_policy.user_access_policy.arn
}

resource "aws_iam_policy_attachment" "user_access_no_vpc_access_policy_attachment" {
  name       = "user_access_no_vpc_access_policy_attachment"
  roles      = [aws_iam_role.user_access_role.name]
  policy_arn = aws_iam_policy.user_no_vpc_access_policy.arn
}

resource "aws_iam_policy_attachment" "user_access_iam_read_only_policy_attachment" {
  name       = "user_access_iam_read_only_policy_attachment"
  roles      = [aws_iam_role.user_access_role.name]
  policy_arn = local.iam_read_only_access_policy_arn
}

resource "aws_iam_policy_attachment" "user_access_power_user_policy_attachment" {
  name       = "user_access_power_user_policy_attachment"
  roles      = [aws_iam_role.user_access_role.name]
  policy_arn = local.power_user_access_policy_arn
}
