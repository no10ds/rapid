output "iam_users" {
  value       = var.iam_users
  description = "The users in the aws account"
}

output "bucket_prefix" {
  value       = var.bucket_prefix
  description = "The prefix used for all the bucktes"
}

output "resource_admin_role_arn" {
  value       = module.iam_resources.resource_admin_role_arn
  description = "The arn of the admin role."
}

output "resource_user_role_arn" {
  value       = module.iam_resources.resource_user_role_arn
  description = "The arn of the user role."
}
