output "athena_query_output_bucket_arn" {
  value       = module.data_workflow.athena_query_result_output_bucket_arn
  description = "Output S3 bucket ARN for Athena query results"
}

output "athena_workgroup_arn" {
  value       = module.data_workflow.athena_workgroup_arn
  description = "Query workgroup for Athena"
}

output "schema_table_arn" {
  value       = module.data_workflow.schema_table_arn
  description = "The ARN of the DynamoDB schema table"
}

output "tags" {
  value       = module.data_workflow.tags
  description = "The tags used in the project"
}
