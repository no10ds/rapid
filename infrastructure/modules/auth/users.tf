# E2E_TEST_CLIENT_USER_ADMIN
resource "aws_cognito_user_pool_client" "e2e_test_client_user_admin" {
  name = "${var.resource-name-prefix}_e2e_test_client_user_admin"

  user_pool_id        = aws_cognito_user_pool.rapid_user_pool.id
  generate_secret     = true
  explicit_auth_flows = var.rapid_client_explicit_auth_flows
  allowed_oauth_scopes = [
    "${aws_cognito_resource_server.rapid_resource_server.identifier}/CLIENT_APP",
  ]
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_flows_user_pool_client = true
}

resource "aws_secretsmanager_secret" "e2e_test_client_user_admin" {
  # checkov:skip=CKV_AWS_149:AWS Managed Key is sufficient
  name                    = "${var.resource-name-prefix}_E2E_TEST_CLIENT_USER_ADMIN"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "e2e_test_client_user_admin_secrets_version" {
  secret_id = aws_secretsmanager_secret.e2e_test_client_user_admin.id
  secret_string = jsonencode({
    CLIENT_NAME   = aws_cognito_user_pool_client.e2e_test_client_user_admin.name
    CLIENT_ID     = aws_cognito_user_pool_client.e2e_test_client_user_admin.id
    CLIENT_SECRET = aws_cognito_user_pool_client.e2e_test_client_user_admin.client_secret
  })
}

# E2E_TEST_CLIENT_DATA_ADMIN
resource "aws_cognito_user_pool_client" "e2e_test_client_data_admin" {
  name = "${var.resource-name-prefix}_e2e_test_client_data_admin"

  user_pool_id        = aws_cognito_user_pool.rapid_user_pool.id
  generate_secret     = true
  explicit_auth_flows = var.rapid_client_explicit_auth_flows
  allowed_oauth_scopes = [
    "${aws_cognito_resource_server.rapid_resource_server.identifier}/CLIENT_APP",
  ]
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_flows_user_pool_client = true
}

resource "aws_secretsmanager_secret" "e2e_test_client_data_admin" {
  # checkov:skip=CKV_AWS_149:AWS Managed Key is sufficient
  name                    = "${var.resource-name-prefix}_E2E_TEST_CLIENT_DATA_ADMIN"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "e2e_test_client_data_admin_secrets_version" {
  secret_id = aws_secretsmanager_secret.e2e_test_client_data_admin.id
  secret_string = jsonencode({
    CLIENT_NAME   = aws_cognito_user_pool_client.e2e_test_client_data_admin.name
    CLIENT_ID     = aws_cognito_user_pool_client.e2e_test_client_data_admin.id
    CLIENT_SECRET = aws_cognito_user_pool_client.e2e_test_client_data_admin.client_secret
  })
}

## E2E_TEST_CLIENT_READ_ALL_WRITE_ALL
resource "aws_cognito_user_pool_client" "e2e_test_client_read_and_write" {
  name = "${var.resource-name-prefix}_e2e_test_client_read_and_write"

  user_pool_id        = aws_cognito_user_pool.rapid_user_pool.id
  generate_secret     = true
  explicit_auth_flows = var.rapid_client_explicit_auth_flows
  allowed_oauth_scopes = [
    "${aws_cognito_resource_server.rapid_resource_server.identifier}/CLIENT_APP",
  ]
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_flows_user_pool_client = true
}

resource "aws_secretsmanager_secret" "e2e_test_client_read_and_write" {
  # checkov:skip=CKV_AWS_149:AWS Managed Key is sufficient
  name                    = "${var.resource-name-prefix}_E2E_TEST_CLIENT_READ_ALL_WRITE_ALL"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "e2e_test_client_read_and_write_secrets_version" {
  secret_id = aws_secretsmanager_secret.e2e_test_client_read_and_write.id
  secret_string = jsonencode({
    CLIENT_NAME   = aws_cognito_user_pool_client.e2e_test_client_read_and_write.name
    CLIENT_ID     = aws_cognito_user_pool_client.e2e_test_client_read_and_write.id
    CLIENT_SECRET = aws_cognito_user_pool_client.e2e_test_client_read_and_write.client_secret
  })
}

# E2E_TEST_CLIENT_WRITE_ALL
resource "aws_cognito_user_pool_client" "e2e_test_client_write_all" {
  name = "${var.resource-name-prefix}_e2e_test_client_write_all"

  user_pool_id        = aws_cognito_user_pool.rapid_user_pool.id
  generate_secret     = true
  explicit_auth_flows = var.rapid_client_explicit_auth_flows
  allowed_oauth_scopes = [
    "${aws_cognito_resource_server.rapid_resource_server.identifier}/CLIENT_APP",
  ]
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_flows_user_pool_client = true
}

resource "aws_secretsmanager_secret" "e2e_test_client_write_all" {
  # checkov:skip=CKV_AWS_149:AWS Managed Key is sufficient
  name                    = "${var.resource-name-prefix}_E2E_TEST_CLIENT_WRITE_ALL"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "e2e_test_client_write_all_secrets_version" {
  secret_id = aws_secretsmanager_secret.e2e_test_client_write_all.id
  secret_string = jsonencode({
    CLIENT_NAME   = aws_cognito_user_pool_client.e2e_test_client_write_all.name
    CLIENT_ID     = aws_cognito_user_pool_client.e2e_test_client_write_all.id
    CLIENT_SECRET = aws_cognito_user_pool_client.e2e_test_client_write_all.client_secret
  })
}

# UI_TEST_USER
resource "random_password" "password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_cognito_user" "ui_test_user" {
  user_pool_id = aws_cognito_user_pool.rapid_user_pool.id
  username     = "${var.resource-name-prefix}_ui_test_user"
  password     = random_password.password.result
}




resource "aws_secretsmanager_secret" "ui_test_user" {
  # checkov:skip=CKV_AWS_149:AWS Managed Key is sufficient
  name                    = "${var.resource-name-prefix}_UI_TEST_USER"
  recovery_window_in_days = 0
}

#
resource "aws_secretsmanager_secret_version" "ui_test_user_secrets_version" {
  secret_id = aws_secretsmanager_secret.ui_test_user.id
  secret_string = jsonencode({
    username     = aws_cognito_user.ui_test_user.username
    subject_name = aws_cognito_user.ui_test_user.username
    password     = aws_cognito_user.ui_test_user.password
    subject_id   = aws_cognito_user.ui_test_user.sub
  })
}
