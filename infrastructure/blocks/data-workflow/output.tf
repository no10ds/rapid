output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}

output "athena_workgroup_arn" {
  value       = module.data_workflow.athena_workgroup_arn
  description = "Query workgroup for Athena"
}

output "athena_query_output_bucket_arn" {
  value       = module.data_workflow.athena_query_result_output_bucket_arn
  description = "Output S3 bucket for Athena query results"
}

output "glue_catalog_arn" {
  value       = module.data_workflow.glue_catalog_arn
  description = "Catalog database arn"
}
