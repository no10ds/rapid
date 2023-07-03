output "resource_admin_role_name" {
  value       = aws_iam_role.admin_access_role.name
  description = "The name of the role users are able to assume to attain admin privileges"
}

output "resource_admin_role_arn" {
  value       = aws_iam_role.admin_access_role.arn
  description = "The ARN of the role users are able to assume to attain admin privileges"
}

output "resource_user_role_name" {
  value       = aws_iam_role.user_access_role.name
  description = "The name of the role users are able to assume to attain user privileges"
}

output "resource_user_role_arn" {
  value       = aws_iam_role.user_access_role.arn
  description = "The ARN of the role users are able to assume to attain user privileges"
}
