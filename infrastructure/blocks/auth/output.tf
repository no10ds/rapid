output "user_pool_endpoint" {
  value       = module.auth.user_pool_endpoint
  description = "The Cognito rapid user pool arn"
}

output "resource_server_scopes" {
  value       = module.auth.resource_server_scopes
  description = "The scopes defined in the resource server"
}

output "rapid_test_client_id" {
  value       = module.auth.rapid_test_client_id
  description = "The rapid test client id registered in the user pool"
}

output "cognito_user_pool_id" {
  value       = module.auth.cognito_user_pool_id
  description = "The Cognito rapid user pool id"
}

output "cognito_client_app_secret_manager_name" {
  value       = module.auth.cognito_client_app_secret_manager_name
  description = "Secret manager name where client app info is stored"
}

output "cognito_user_app_secret_manager_name" {
  value       = module.auth.cognito_user_app_secret_manager_name
  description = "Secret manager name where user login app info is stored"
}

output "user_permission_table_name" {
  value       = module.auth.user_permission_table_name
  description = "Tha name of the dynamoDB table that stores permissions"
}

output "user_permission_table_arn" {
  value       = module.auth.user_permission_table_arn
  description = "The arn of the dynamoDB table that stores permissions"
}
