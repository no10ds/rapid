output "admin_group_names" {
  value       = values(aws_iam_group.groups)[*].name
  description = "The names of the admin groups"
}

output "user_group_names" {
  value       = values(aws_iam_group.groups)[*].name
  description = "The name of the user groups"
}
