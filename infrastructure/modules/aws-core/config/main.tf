data "aws_iam_policy_document" "config_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "config" {
  name = var.iam_role_name

  assume_role_policy = data.aws_iam_policy_document.config_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "config" {
  role       = aws_iam_role.config.name
  policy_arn = local.config_policy_arn
}

data "aws_iam_policy_document" "allow_s3_access_for_aws_config_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetBucketAcl"]
    resources = [var.enable_lifecycle_management_for_s3 ? aws_s3_bucket.config_with_lifecycle[0].arn : aws_s3_bucket.config_without_lifecycle[0].arn]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["true"]
    }
  }

  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${var.enable_lifecycle_management_for_s3 ? aws_s3_bucket.config_with_lifecycle[0].arn : aws_s3_bucket.config_without_lifecycle[0].arn}/${var.bucket_key_prefix}/AWSLogs/${local.bucket_account_id}/Config/*"]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["true"]
    }

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

resource "aws_iam_policy" "allow_s3_access_for_aws_config_policy" {
  name   = "allow_s3_access_for_aws_config_policy"
  policy = data.aws_iam_policy_document.allow_s3_access_for_aws_config_policy_document.json
}

resource "aws_iam_role_policy_attachment" "allow_s3_access_for_aws_config_attachment" {
  role       = aws_iam_role.config.name
  policy_arn = aws_iam_policy.allow_s3_access_for_aws_config_policy.arn
}

# S3 buckets
resource "aws_s3_bucket" "config_with_lifecycle" {
  # checkov:skip=CKV_AWS_144:No need for cross region replication
  # checkov:skip=CKV_AWS_18:No need for logging

  count         = var.enable_lifecycle_management_for_s3 ? 1 : 0
  bucket_prefix = var.bucket_prefix
  acl           = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.s3_kms_sse_encryption_key_arn
        sse_algorithm     = "aws:kms"
      }
    }
  }

  versioning {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true

  }

  lifecycle_rule {
    enabled = true
    prefix  = "${var.bucket_key_prefix}/"

    expiration {
      days = 365
    }

    noncurrent_version_expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_public_access_block" "config_with_lifecycle" {
  count                   = var.enable_lifecycle_management_for_s3 ? 1 : 0
  bucket                  = aws_s3_bucket.config_with_lifecycle[0].id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket" "config_without_lifecycle" {
  # checkov:skip=CKV_AWS_144:No need for cross region replication
  # checkov:skip=CKV_AWS_18:No need for logging

  count         = var.enable_lifecycle_management_for_s3 ? 0 : 1
  bucket_prefix = var.bucket_prefix
  acl           = "private"

  force_destroy = true

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.s3_kms_sse_encryption_key_arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "config_without_lifecycle" {
  count                   = var.enable_lifecycle_management_for_s3 ? 0 : 1
  bucket                  = aws_s3_bucket.config_without_lifecycle[0].id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_config_configuration_recorder" "config" {
  name     = var.config_recorder_name
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

resource "aws_config_delivery_channel" "config" {
  name           = var.config_delivery_channel_name
  s3_bucket_name = var.enable_lifecycle_management_for_s3 ? aws_s3_bucket.config_with_lifecycle[0].bucket : aws_s3_bucket.config_without_lifecycle[0].bucket
  s3_key_prefix  = var.bucket_key_prefix

  snapshot_delivery_properties {
    delivery_frequency = var.delivery_frequency
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_configuration_recorder_status" "config" {
  name       = aws_config_configuration_recorder.config.name
  is_enabled = true

  depends_on = [aws_config_delivery_channel.config]
}

resource "aws_config_config_rule" "instances_in_vpc" {
  name = "instances_in_vpc"

  source {
    owner             = "AWS"
    source_identifier = "INSTANCES_IN_VPC"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "ec2_volume_inuse_check" {
  name = "ec2_volume_inuse_check"

  source {
    owner             = "AWS"
    source_identifier = "EC2_VOLUME_INUSE_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "eip_attached" {
  name = "eip_attached"

  source {
    owner             = "AWS"
    source_identifier = "EIP_ATTACHED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "encrypted_volumes" {
  name = "encrypted_volumes"

  source {
    owner             = "AWS"
    source_identifier = "ENCRYPTED_VOLUMES"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "incoming_ssh_disabled" {
  name = "incoming_ssh_disabled"

  source {
    owner             = "AWS"
    source_identifier = "INCOMING_SSH_DISABLED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "cloud_trail_enabled" {
  name = "cloud_trail_enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "cloudwatch_alarm_action_check" {
  name = "cloudwatch_alarm_action_check"

  source {
    owner             = "AWS"
    source_identifier = "CLOUDWATCH_ALARM_ACTION_CHECK"
  }

  input_parameters = jsonencode({
    alarmActionRequired            = "true"
    insufficientDataActionRequired = "false"
    okActionRequired               = "false"
  })

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "iam_group_has_users_check" {
  name = "iam_group_has_users_check"

  source {
    owner             = "AWS"
    source_identifier = "IAM_GROUP_HAS_USERS_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

//see https://docs.aws.amazon.com/config/latest/developerguide/iam-password-policy.html
resource "aws_config_config_rule" "iam_password_policy" {
  name = "iam_password_policy"

  source {
    owner             = "AWS"
    source_identifier = "IAM_PASSWORD_POLICY"
  }

  input_parameters = jsonencode(
    {
      RequireUppercaseCharacters = local.password_policy["require_uppercase_characters"]
      RequireLowercaseCharacters = local.password_policy["require_lowercase_characters"]
      RequireSymbols             = local.password_policy["require_symbols"]
      RequireNumbers             = local.password_policy["require_numbers"]
      MinimumPasswordLength      = local.password_policy["minimum_password_length"]
      PasswordReusePrevention    = local.password_policy["password_reuse_prevention"]
      MaxPasswordAge             = local.password_policy["max_password_age"]
    }
  )

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "iam_user_group_membership_check" {
  name = "iam_user_group_membership_check"

  source {
    owner             = "AWS"
    source_identifier = "IAM_USER_GROUP_MEMBERSHIP_CHECK"
  }

  input_parameters = jsonencode(var.iam_user_groups)

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "iam_user_no_policies_check" {
  name = "iam_user_no_policies_check"

  source {
    owner             = "AWS"
    source_identifier = "IAM_USER_NO_POLICIES_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "root_account_mfa_enabled" {
  name = "root_account_mfa_enabled"

  source {
    owner             = "AWS"
    source_identifier = "ROOT_ACCOUNT_MFA_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "s3_bucket_public_read_prohibited" {
  name = "s3_bucket_public_read_prohibited"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "s3_bucket_public_write_prohibited" {
  name = "s3_bucket_public_write_prohibited"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_PUBLIC_WRITE_PROHIBITED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "s3_bucket_ssl_requests_only" {
  name = "s3_bucket_ssl_requests_only"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_SSL_REQUESTS_ONLY"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "s3_bucket_server_side_encryption_enabled" {
  name = "s3_bucket_server_side_encryption_enabled"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "s3_bucket_versioning_enabled" {
  name = "s3_bucket_versioning_enabled"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_VERSIONING_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "ebs_optimized_instance" {
  name = "ebs_optimized_instance"

  source {
    owner             = "AWS"
    source_identifier = "EBS_OPTIMIZED_INSTANCE"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "access_key_rotated" {
  name = "access_key_rotated"

  source {
    owner             = "AWS"
    source_identifier = "ACCESS_KEYS_ROTATED"
  }

  input_parameters = jsonencode({
    maxAccessKeyAge = var.max_access_key_age
  })

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "approved_amis_by_tag" {
  count = length(var.amis_by_tag_key_and_value_list) > 0 ? 1 : 0
  name  = "approved_amis_by_tag"

  source {
    owner             = "AWS"
    source_identifier = "APPROVED_AMIS_BY_TAG"
  }

  input_parameters = jsonencode({
    amisByTagKeyAndValue = var.amis_by_tag_key_and_value_list
  })

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "autoscaling_group_elb_healthcheck_required" {
  name = "autoscaling_group_elb_healthcheck_required"

  source {
    owner             = "AWS"
    source_identifier = "AUTOSCALING_GROUP_ELB_HEALTHCHECK_REQUIRED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "desired_instance_type" {
  count = length(var.desired_instance_types) > 0 ? 1 : 0
  name  = "desired_instance_type"

  source {
    owner             = "AWS"
    source_identifier = "DESIRED_INSTANCE_TYPE"
  }

  input_parameters = jsonencode({
    InstanceType = var.desired_instance_types
  })

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "rds_instance_public_access_check" {
  name = "rds_instance_public_access_check"

  source {
    owner             = "AWS"
    source_identifier = "RDS_INSTANCE_PUBLIC_ACCESS_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "rds_snapshots_public_prohibited" {
  name = "rds_snapshots_public_prohibited"

  source {
    owner             = "AWS"
    source_identifier = "RDS_SNAPSHOTS_PUBLIC_PROHIBITED"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "iam_policy_no_statements_with_admin_access" {
  name = "iam_policy_no_statements_with_admin_access"

  source {
    owner             = "AWS"
    source_identifier = "IAM_POLICY_NO_STATEMENTS_WITH_ADMIN_ACCESS"
  }

  depends_on = [aws_config_configuration_recorder.config]
}

resource "aws_config_config_rule" "iam_root_access_key_check" {
  name = "iam_root_access_key_check"

  source {
    owner             = "AWS"
    source_identifier = "IAM_ROOT_ACCESS_KEY_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.config]
}
