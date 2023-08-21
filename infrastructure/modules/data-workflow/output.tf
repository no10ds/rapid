output "athena_query_result_output_bucket_arn" {
  value       = aws_s3_bucket.rapid_athena_query_results_bucket.arn
  description = "Output S3 bucket ARN for Athena query results"
}

output "athena_workgroup_arn" {
  value       = aws_athena_workgroup.rapid_athena_workgroup.arn
  description = "Query workgroup for Athena"
}

output "schema_table_arn" {
  value       = aws_dynamodb_table.schema_table.arn
  description = "The ARN of the DynamoDB schema table"
}

output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}
