resource "aws_s3_bucket" "rapid_athena_query_results_bucket" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key
  #checkov:skip=CKV_AWS_21:No need to version query results
  #checkov:skip=CKV_AWS_18:No need to log query results
  bucket = "${var.resource-name-prefix}-aws-athena-query-results-${var.aws_account}"
  acl    = "private"

  tags = var.tags

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "expiry_config"
    enabled = true
    expiration {
      days = 7
    }
  }
}
#TODO: add aws_s3_bucket_lifecycle_configuration and aws_s3_bucket_server_side_encryption_configuration instead - current config DEPRECIATED
#resource "aws_s3_bucket_lifecycle_configuration" "rapid_athena_query_results_bucket_life_cycle" {
#  bucket = aws_s3_bucket.rapid_athena_query_results_bucket.id
#
#  rule {
#    id = "expiry_config"
#    status = Enabled
#    expiration {
#      days = 30
#    }
#  }
#
#}

resource "aws_s3_bucket_public_access_block" "rapid_athena_query_results_bucket" {
  bucket                  = aws_s3_bucket.rapid_athena_query_results_bucket.id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_athena_workgroup" "rapid_athena_workgroup" {
  name          = "${var.resource-name-prefix}_athena_workgroup"
  force_destroy = true

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.rapid_athena_query_results_bucket.bucket}"

      encryption_configuration {
        encryption_option = "SSE_S3"
        # kms_key_arn = ""
      }
    }
  }

  tags = var.tags
}

resource "aws_s3_bucket_policy" "athena_query_bucket_policy" {
  bucket = aws_s3_bucket.rapid_athena_query_results_bucket.id
  policy = <<POLICY
    {
        "Version": "2012-10-17",
        "Statement": [
            {
              "Sid": "AllowSSLRequestsOnly",
              "Action": "s3:*",
              "Effect": "Deny",
              "Resource": [
                "${aws_s3_bucket.rapid_athena_query_results_bucket.arn}/*",
                "${aws_s3_bucket.rapid_athena_query_results_bucket.arn}"
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
