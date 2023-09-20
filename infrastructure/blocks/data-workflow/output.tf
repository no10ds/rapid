output "athena_query_output_bucket_arn" {
  value       = module.data_workflow.athena_query_result_output_bucket_arn
  description = "Output S3 bucket ARN for Athena query results"
}

output "athena_workgroup_arn" {
  value       = module.data_workflow.athena_workgroup_arn
  description = "The ARN of the Query workgroup for Athena"
}

output "athena_workgroup_name" {
  value       = module.data_workflow.athena_workgroup_name
  description = "The name of the Query workgroup for Athena"
}

output "schema_table_arn" {
  value       = module.data_workflow.schema_table_arn
  description = "The ARN of the DynamoDB schema table"
}

output "catalogue_db_name" {
  value       = module.data_workflow.catalogue_db_name
  description = "The name of the Glue Catalogue database"
}

output "tags" {
  value       = module.data_workflow.tags
  description = "The tags used in the project"
}
