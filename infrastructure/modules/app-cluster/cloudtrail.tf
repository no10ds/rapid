data "aws_iam_policy_document" "access_logs_key_policy" {

  statement {
    sid = "Enable IAM User Permissions"

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions = [
      "kms:Describe*",
      "kms:List*",
      "kms:Get*",
      "kms:Put*",
      "kms:GenerateDataKey*",
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
    ]

    resources = [
      "arn:aws:kms:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:key/*",
    ]
  }

  statement {
    sid = "Enable Logs Encryption Permissions"

    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["logs.${data.aws_region.region.name}.amazonaws.com"]
    }

    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*",
    ]

    resources = [
      "arn:aws:kms:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:key/*",
    ]

    condition {
      test     = "ArnEquals"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values = [
        "arn:aws:logs:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:log-group:${var.resource-name-prefix}_access_logs"
      ]
    }
  }

  statement {
    sid = "Enable CloudTrail Encryption Permissions"

    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*",
    ]

    resources = [
      "arn:aws:kms:${data.aws_region.region.name}:${data.aws_caller_identity.current.account_id}:key/*",
    ]
  }
}

resource "aws_kms_key" "access_logs_key" {
  count               = var.enable_cloudtrail ? 1 : 0
  description         = "This key is used to encrypt the access log objects"
  policy              = data.aws_iam_policy_document.access_logs_key_policy.json
  tags                = var.tags
  enable_key_rotation = true
}

resource "aws_cloudwatch_log_group" "access_logs_log_group" {
  count             = var.enable_cloudtrail ? 1 : 0
  depends_on        = [aws_kms_key.access_logs_key]
  name              = "${var.resource-name-prefix}_access_logs"
  retention_in_days = 90
  kms_key_id        = aws_kms_key.access_logs_key[0].arn
  tags              = var.tags
}

resource "aws_iam_role" "cloud_trail_role" {
  count = var.enable_cloudtrail ? 1 : 0
  name  = "${var.resource-name-prefix}-cloudtrail-cloudwatch-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

  tags = var.tags
}

resource "aws_iam_policy" "aws_iam_policy_cloudtrail_cloudwatch" {
  count = var.enable_cloudtrail ? 1 : 0
  name  = "${var.resource-name-prefix}-iam-policy-cloudtrail-cloudwatch"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailCreateLogStream2014110",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream"
            ],
            "Resource": [
                "${aws_cloudwatch_log_group.access_logs_log_group[0].arn}:*"
            ]
        },
        {
            "Sid": "AWSCloudTrailPutLogEvents20141101",
            "Effect": "Allow",
            "Action": [
                "logs:PutLogEvents"
            ],
            "Resource": [
                "${aws_cloudwatch_log_group.access_logs_log_group[0].arn}:*"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_policy_attachment" "aws_iam_policy_cloudtrail_cloudwatch_attachment" {
  count      = var.enable_cloudtrail ? 1 : 0
  name       = "${var.resource-name-prefix}-iam-policy-cloudtrail-cloudwatch-attachment"
  policy_arn = aws_iam_policy.aws_iam_policy_cloudtrail_cloudwatch[0].arn
  roles      = [aws_iam_role.cloud_trail_role[0].id]
}


resource "aws_s3_bucket" "access_logs" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key
  #checkov:skip=CKV_AWS_19:No need for securely encrypted at rest
  count         = var.enable_cloudtrail ? 1 : 0
  bucket        = "${var.resource-name-prefix}-access-logs"
  force_destroy = true
  tags          = var.tags

  versioning {
    enabled = true
  }

  logging {
    target_bucket = var.log_bucket_name
    target_prefix = "log/${var.resource-name-prefix}-cloudtrail-access-logs"
  }
}

resource "aws_s3_bucket_public_access_block" "access_logs" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.access_logs[0].id

  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_policy" "access_logs_bucket_policy" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.access_logs[0].id
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "${aws_s3_bucket.access_logs[0].arn}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "${aws_s3_bucket.access_logs[0].arn}/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        },
        {
          "Sid": "AllowSSLRequestsOnly",
          "Action": "s3:*",
          "Effect": "Deny",
          "Resource": [
            "${aws_s3_bucket.access_logs[0].arn}/*",
            "${aws_s3_bucket.access_logs[0].arn}"
          ],
          "Condition": {
            "Bool": {
              "aws:SecureTransport": "false"
            }
          },
          "Principal": "*"
        }
    ]
}
POLICY
}

resource "aws_s3_bucket_lifecycle_configuration" "access_logs_lifecycle" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.access_logs[0].id

  rule {
    id     = "expire-old-logs"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "access_logs_s3_encryption_config" {
  count      = var.enable_cloudtrail ? 1 : 0
  depends_on = [aws_kms_key.access_logs_key]
  bucket     = aws_s3_bucket.access_logs[0].bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.access_logs_key[0].arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_cloudtrail" "access_logs_trail" {
  # checkov:skip=CKV_AWS_252:No need for an SNS topic
  count = var.enable_cloudtrail ? 1 : 0
  depends_on = [
    aws_s3_bucket_policy.access_logs_bucket_policy, # Policy for S3 that cloudtrail dumps too
    aws_kms_key.access_logs_key
  ]

  name = "${var.resource-name-prefix}-access-logs"

  s3_bucket_name = aws_s3_bucket.access_logs[0].id
  s3_key_prefix  = "db-access-logs"

  kms_key_id = aws_kms_key.access_logs_key[0].arn

  is_multi_region_trail         = true
  enable_log_file_validation    = true
  include_global_service_events = true

  event_selector {
    include_management_events = false

    data_resource {
      type = "AWS::DynamoDB::Table"

      values = [
        aws_dynamodb_table.service_table.arn,
        var.permissions_table_arn
      ]
    }
  }

  # CloudTrail requires the Log Stream wildcard
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.access_logs_log_group[0].arn}:*" # Needs to be created
  cloud_watch_logs_role_arn  = aws_iam_role.cloud_trail_role[0].arn

  tags = var.tags
}
