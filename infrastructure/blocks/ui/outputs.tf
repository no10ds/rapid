output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}

output "bucket_public_arn" {
  value       = module.ui.bucket_public_arn
  description = "The arn of the public S3 bucket"
}

output "bucket_website_domain" {
  value       = module.ui.bucket_website_domain
  description = "The domain of the website endpoint"
}
