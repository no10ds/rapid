data "aws_region" "region" {}
data "aws_caller_identity" "current" {}

resource "aws_dynamodb_table" "permissions_table" {
  # checkov:skip=CKV_AWS_119:No need for customer managed keys
  name         = "${var.resource-name-prefix}_${var.permissions_table_name}"
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

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = var.tags
}

resource "aws_dynamodb_table_item" "data_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  for_each = local.data_permissions

  item = <<ITEM
      {
        "PK": {"S": "PERMISSION"},
        "SK": {"S": "${each.key}"},
        "Id": {"S": "${each.key}"},
        "Type": {"S": "${each.value.type}"},
        "Sensitivity": {"S": "${each.value.sensitivity}"},
        "Layer": {"S": "${each.value.layer}"}
      }
    ITEM
}

resource "aws_dynamodb_table_item" "admin_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  for_each = var.admin_permissions

  item = <<ITEM
      {
        "PK": {"S": "PERMISSION"},
        "SK": {"S": "${each.key}"},
        "Id": {"S": "${each.key}"},
        "Type": {"S": "${each.value.type}"}
      }
    ITEM
}

resource "aws_dynamodb_table_item" "test_client_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  item = <<ITEM
  {
    "PK": {"S": "SUBJECT"},
    "SK": {"S": "${aws_cognito_user_pool_client.test_client.id}"},
    "Id": {"S": "${aws_cognito_user_pool_client.test_client.id}"},
    "Type": {"S": "CLIENT"},
    "Permissions": {"SS": ["DATA_ADMIN","READ_ALL","USER_ADMIN","WRITE_ALL"]}
  }
  ITEM
}

resource "aws_dynamodb_table_item" "test_client_write_all_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  item = <<ITEM
  {
    "PK": {"S": "SUBJECT"},
    "SK": {"S": "${aws_cognito_user_pool_client.e2e_test_client_write_all.id}"},
    "Id": {"S": "${aws_cognito_user_pool_client.e2e_test_client_write_all.id}"},
    "Type": {"S": "CLIENT"},
    "Permissions": {"SS": ["WRITE_ALL"]}
  }
  ITEM
}

resource "aws_dynamodb_table_item" "test_client_read_and_write_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  item = <<ITEM
  {
    "PK": {"S": "SUBJECT"},
    "SK": {"S": "${aws_cognito_user_pool_client.e2e_test_client_read_and_write.id}"},
    "Id": {"S": "${aws_cognito_user_pool_client.e2e_test_client_read_and_write.id}"},
    "Type": {"S": "CLIENT"},
    "Permissions": {"SS": ["READ_ALL","WRITE_ALL"]}
  }
  ITEM
}

resource "aws_dynamodb_table_item" "test_client_data_admin_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  item = <<ITEM
  {
    "PK": {"S": "SUBJECT"},
    "SK": {"S": "${aws_cognito_user_pool_client.e2e_test_client_data_admin.id}"},
    "Id": {"S": "${aws_cognito_user_pool_client.e2e_test_client_data_admin.id}"},
    "Type": {"S": "CLIENT"},
    "Permissions": {"SS": ["DATA_ADMIN","USER_ADMIN"]}
  }
  ITEM
}

resource "aws_dynamodb_table_item" "test_client_user_admin_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  item = <<ITEM
  {
    "PK": {"S": "SUBJECT"},
    "SK": {"S": "${aws_cognito_user_pool_client.e2e_test_client_user_admin.id}"},
    "Id": {"S": "${aws_cognito_user_pool_client.e2e_test_client_user_admin.id}"},
    "Type": {"S": "CLIENT"},
    "Permissions": {"SS": ["USER_ADMIN"]}
  }
  ITEM
}

resource "aws_dynamodb_table_item" "ui_test_user_permissions" {
  table_name = aws_dynamodb_table.permissions_table.name
  hash_key   = aws_dynamodb_table.permissions_table.hash_key
  range_key  = aws_dynamodb_table.permissions_table.range_key

  item = <<ITEM
  {
    "PK": {"S": "SUBJECT"},
    "SK": {"S": "${aws_cognito_user.ui_test_user.sub}"},
    "Id": {"S": "${aws_cognito_user.ui_test_user.sub}"},
    "Type": {"S": "USER"},
    "Permissions": {"SS": ["DATA_ADMIN","READ_ALL","USER_ADMIN","WRITE_ALL"]}
  }
  ITEM
}
