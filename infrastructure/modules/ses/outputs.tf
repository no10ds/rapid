output "ses_arn" {
  value       = aws_ses_domain_identity.ses_domain[*].arn
  description = "SES service list of arns"
}
