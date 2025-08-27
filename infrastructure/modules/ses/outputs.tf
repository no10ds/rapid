output "ses_arn" {
  value       = aws_ses_domain_identity.ses_domain[0].arn
  description = "SES service arn"
}
