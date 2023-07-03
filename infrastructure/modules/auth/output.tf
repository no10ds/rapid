output "user_pool_endpoint" {
  value       = aws_cognito_user_pool.rapid_user_pool.endpoint
  description = "The Cognito rapid user pool endpoint"
}

output "resource_server_scopes" {
  value       = aws_cognito_resource_server.rapid_resource_server.scope_identifiers
  description = "The scopes defined in the resource server"
}

output "rapid_test_client_id" {
  value       = aws_cognito_user_pool_client.test_client.id
  description = "The rapid test client id registered in the user pool"
}

output "cognito_user_pool_id" {
  value       = aws_cognito_user_pool.rapid_user_pool.id
  description = "The Cognito rapid user pool id"
}

output "cognito_client_app_secret_manager_name" {
  value       = aws_secretsmanager_secret.client_secrets_cognito.name
  description = "Secret manager name where client app info is stored"
}

output "cognito_user_app_secret_manager_name" {
  value       = aws_secretsmanager_secret.user_secrets_cognito.name
  description = "Secret manager name where user login app info is stored"
}

output "user_permission_table_name" {
  value       = aws_dynamodb_table.permissions_table.name
  description = "The name of the dynamoDB table that stores permissions"
}

output "user_permission_table_arn" {
  value       = aws_dynamodb_table.permissions_table.arn
  description = "The arn of the dynamoDB table that stores permissions"
}
