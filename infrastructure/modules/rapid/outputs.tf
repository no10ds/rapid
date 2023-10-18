output "athena_workgroup_name" {
  value       = module.data_workflow.athena_workgroup_name
  description = "The name of the Query workgroup for Athena"
}

output "catalogue_db_name" {
  value       = module.data_workflow.catalogue_db_name
  description = "The name of the Glue Catalogue database"
}
