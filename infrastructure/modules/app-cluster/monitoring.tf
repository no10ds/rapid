resource "aws_cloudwatch_log_metric_filter" "rapid-service-log-error-count" {
  name           = "rapid-service-log-error-count"
  pattern        = "ERROR"
  log_group_name = aws_cloudwatch_log_group.log-group.name
  metric_transformation {
    name          = "rapid-log-count-errors"
    namespace     = "rapid-metric"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_sns_topic" "log-error-alarm-notification" {
  name              = "${var.resource-name-prefix}-log-error-alarm-notification"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_cloudwatch_metric_alarm" "log-error-alarm" {
  alarm_name          = "${var.resource-name-prefix}-log-error-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "rapid-log-count-errors"
  namespace           = "rapid-metric"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_actions       = [aws_sns_topic.log-error-alarm-notification.arn]
  alarm_description   = "Triggered everytime a log error occurs in the application. Send email notification"
}

resource "aws_sns_topic_subscription" "log-error-alarm-subscription" {
  count     = length(var.support_emails_for_cloudwatch_alerts)
  topic_arn = aws_sns_topic.log-error-alarm-notification.arn
  protocol  = "email"
  endpoint  = var.support_emails_for_cloudwatch_alerts[count.index]
}
