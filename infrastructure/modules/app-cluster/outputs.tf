output "ecs_cluster_arn" {
  value       = aws_ecs_cluster.aws-ecs-cluster.arn
  description = "Cluster identifier"
}

output "ecs_task_execution_role_arn" {
  value       = aws_iam_role.ecsTaskExecutionRole.arn
  description = "The ECS task execution role ARN"
}

output "load_balancer_dns" {
  value       = aws_alb.application_load_balancer.dns_name
  description = "The DNS name of the load balancer"
}

output "hosted_zone_id" {
  value = var.hosted_zone_id == "" ? aws_route53_zone.primary-hosted-zone[0].zone_id : ""
}

output "hosted_zone_name_servers" {
  value       = var.hosted_zone_id == "" ? aws_route53_zone.primary-hosted-zone[0].name_servers : []
  description = "Name servers of the primary hosted zone linked to the domain"
}

output "load_balancer_arn" {
  value       = aws_alb.application_load_balancer.arn
  description = "The arn of the load balancer"
}

output "log_error_alarm_notification_arn" {
  value       = aws_sns_topic.log-error-alarm-notification.arn
  description = "The arn of the sns topic that receives notifications on log error alerts"
}

output "rapid_metric_log_error_alarm_arn" {
  value       = aws_cloudwatch_metric_alarm.log-error-alarm.arn
  description = "The arn of the log error alarm metric"
}

output "route_53_validation_record_fqdns" {
  value       = [for record in aws_route53_record.rapid_validation_record : record.fqdn]
  description = "The fqdns of the route53 validation records for the certificate"
}

output "service_table_arn" {
  value       = aws_dynamodb_table.service_table.arn
  description = "The arn of the dynamoDB table that stores the user service"
}

output "application_version" {
  value = var.application_version
}
