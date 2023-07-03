data "aws_region" "region" {}
data "aws_caller_identity" "current" {}

resource "aws_dynamodb_table" "service_table" {
  # checkov:skip=CKV_AWS_119:No need for customer managed keys
  name         = "${var.resource-name-prefix}_service_table"
  hash_key     = "PK"
  range_key    = "SK"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "SK2"
    type = "S"
  }

  global_secondary_index {
    name            = "JOB_SUBJECT_ID"
    hash_key        = "PK"
    range_key       = "SK2"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = var.tags
}
