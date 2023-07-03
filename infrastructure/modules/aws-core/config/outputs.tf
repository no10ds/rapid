output "config_s3_bucket_id" {
  description = "The ID of the S3 bucket AWS Config writes its findings into"
  value       = var.enable_lifecycle_management_for_s3 ? aws_s3_bucket.config_with_lifecycle[0].id : aws_s3_bucket.config_without_lifecycle[0].id
}
