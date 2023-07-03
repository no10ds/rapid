output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}

output "ecr_private_repo_arn" {
  value       = aws_ecr_repository.private.arn
  description = "The arn of the private ecr repo"
}

output "ecr_private_ckan_repo_arn" {
  value       = aws_ecr_repository.private_ckan.arn
  description = "The arn of the private ckan ecr repo"
}

output "ecr_public_repo_arn" {
  value       = aws_ecrpublic_repository.public.arn
  description = "The arn of the public ecr repo"
}

output "ecr_public_ckan_repo_arn" {
  value       = aws_ecrpublic_repository.public_ckan.arn
  description = "The arn of the public ckan ecr repo"
}
