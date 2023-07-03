output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.rapid_data_storage.arn
  description = "The ARN of the S3 bucket"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.rapid_data_storage.id
  description = "The bucket name of the S3 bucket"
}

output "s3_bucket_prefix" {
  value       = aws_s3_bucket.rapid_data_storage.bucket_prefix
  description = "The bucket_prefix of the S3 bucket"
}

output "log_bucket_name" {
  value       = aws_s3_bucket.logs.id
  description = "The name of the log bucket"
}
