resource "aws_dynamodb_table" "schema_table" {
  # checkov:skip=CKV_AWS_119:No need for customer managed keys
  name           = "${var.resource-name-prefix}_schema_table"
  hash_key       = "PK"
  range_key      = "SK"
  billing_mode   = "PAY_PER_REQUEST"
  stream_enabled = true
  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "N"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = var.tags
}
