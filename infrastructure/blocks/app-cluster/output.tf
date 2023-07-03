output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}

output "load_balancer_dns" {
  value       = module.app_cluster.load_balancer_dns
  description = "The DNS name of the load balancer"
}

output "ecs_cluster_arn" {
  value       = module.app_cluster.ecs_cluster_arn
  description = "Cluster identifier"
}

output "load_balancer_arn" {
  value       = module.app_cluster.load_balancer_arn
  description = "The arn of the load balancer"
}

output "hosted_zone_name_servers" {
  value       = module.app_cluster.hosted_zone_name_servers
  description = "Name servers of the primary hosted zone linked to the domain"
}

output "hosted_zone_id" {
  value       = module.app_cluster.hosted_zone_id
  description = "id of the primary hosted zone linked to the domain"
}

output "ecs_task_execution_role_arn" {
  value       = module.app_cluster.ecs_task_execution_role_arn
  description = "The ECS task execution role ARN"
}

output "log_error_alarm_notification_arn" {
  value       = module.app_cluster.log_error_alarm_notification_arn
  description = "The arn of the sns topic that receives notifications on log error alerts"
}

output "rapid_metric_log_error_alarm_arn" {
  value       = module.app_cluster.rapid_metric_log_error_alarm_arn
  description = "The arn of the log error alarm metric"
}

output "service_table_arn" {
  value       = module.app_cluster.service_table_arn
  description = "The arn of the dynamoDB table that stores the user service"
}
