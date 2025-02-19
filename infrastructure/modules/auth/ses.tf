locals {
  allowed_email_domains   = concat(["simulator.amazonses.com"], split(",", var.allowed_email_domains))
  ses_allowed_from_emails = concat(["no-reply@${var.domain_name}"], var.ses_allowed_from_emails)
}
resource "aws_ses_domain_identity" "ses_domain" {
  count  = var.cognito_ses_authentication ? 1 : 0
  domain = var.domain_name
}

resource "aws_ses_domain_mail_from" "main" {
  count            = var.cognito_ses_authentication ? 1 : 0
  domain           = aws_ses_domain_identity.ses_domain[0].domain
  mail_from_domain = "mail.${var.domain_name}"
}

# Route53 CNAME dkim records
resource "aws_ses_domain_dkim" "ses_domain_dkim" {
  count  = var.cognito_ses_authentication ? 1 : 0
  domain = join("", aws_ses_domain_identity.ses_domain[0].*.domain)
}

resource "aws_route53_record" "amazonses_dkim_record" {
  count   = var.cognito_ses_authentication ? 3 : 0
  zone_id = var.hosted_zone_id
  name    = "${element(aws_ses_domain_dkim.ses_domain_dkim[0].dkim_tokens, count.index)}._domainkey.${var.domain_name}"
  type    = "CNAME"
  ttl     = "600"
  records = ["${element(aws_ses_domain_dkim.ses_domain_dkim[0].dkim_tokens, count.index)}.dkim.amazonses.com"]
}

# Route53 TXT verification record
resource "aws_ses_domain_identity_verification" "verification" {
  count  = var.cognito_ses_authentication ? 1 : 0
  domain = aws_ses_domain_identity.ses_domain[0].domain

  depends_on = [aws_route53_record.amazonses_verification_record]
}

resource "aws_route53_record" "amazonses_verification_record" {
  count   = var.cognito_ses_authentication ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = "_amazonses.${aws_ses_domain_identity.ses_domain[0].domain}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.ses_domain[0].verification_token]
}

# Route53 MX record
resource "aws_route53_record" "ses_domain_mail_from_mx" {
  count   = var.cognito_ses_authentication ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = aws_ses_domain_mail_from.main[0].mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.${var.aws_region}.amazonses.com"]
}

# Route53 TXT record for SPF
resource "aws_route53_record" "ses_domain_mail_from_txt" {
  count   = var.cognito_ses_authentication ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = aws_ses_domain_mail_from.main[0].mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com ~all"]
}

# Route53 TXT record for DMARC
resource "aws_route53_record" "dmarc" {
  count   = var.cognito_ses_authentication ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = "_dmarc.${aws_ses_domain_identity.ses_domain[0].domain}"
  type    = "TXT"
  ttl     = "600"
  records = ["v=DMARC1; p=none;"]
}

# SNS topic for bounce and complaint emails
resource "aws_ses_identity_notification_topic" "bounce" {
  count                    = var.cognito_ses_authentication ? 1 : 0
  topic_arn                = aws_sns_topic.ses_notifications[0].arn
  notification_type        = "Bounce"
  identity                 = aws_ses_domain_identity.ses_domain[0].domain
  include_original_headers = true
}

resource "aws_ses_identity_notification_topic" "complaint" {
  count                    = var.cognito_ses_authentication ? 1 : 0
  topic_arn                = aws_sns_topic.ses_notifications[0].arn
  notification_type        = "Complaint"
  identity                 = aws_ses_domain_identity.ses_domain[0].domain
  include_original_headers = true
}

resource "aws_sns_topic" "ses_notifications" {
  count = var.cognito_ses_authentication ? 1 : 0
  name  = "${var.resource-name-prefix}_ses_bounce_complaint_notifications"
  tags  = var.tags
}

resource "aws_sns_topic_policy" "default" {
  arn    = aws_sns_topic.ses_notifications[0].arn
  policy = data.aws_iam_policy_document.sns_topic_policy[0].json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  count = var.cognito_ses_authentication ? 1 : 0
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["ses.amazonaws.com"]
    }
    resources = [
      aws_sns_topic.ses_notifications[0].arn,
    ]
    condition {
      test     = "StringEquals"
      values   = [var.aws_account]
      variable = "AWS:SourceAccount"
    }
    condition {
      test     = "StringEquals"
      values   = [aws_ses_domain_identity.ses_domain[0].arn]
      variable = "AWS:SourceArn"
    }

    sid = "__default_policy_ID"
  }

  statement {
    actions = [
      "SNS:Subscribe",
      "SNS:SetTopicAttributes",
      "SNS:RemovePermission",
      "SNS:Receive",
      "SNS:Publish",
      "SNS:ListSubscriptionsByTopic",
      "SNS:GetTopicAttributes",
      "SNS:DeleteTopic",
      "SNS:AddPermission",
    ]

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [var.aws_account]
    }

    resources = [
      aws_sns_topic.ses_notifications[0].arn,
    ]

    condition {
      test     = "StringEquals"
      values   = [aws_sns_topic.ses_notifications[0].arn]
      variable = "AWS:SourceArn"
    }

    sid = "AWSEvents"
  }

}

resource "aws_sns_topic_subscription" "email_subscription" {
  count     = var.cognito_ses_authentication ? length(var.ses_email_notifications) : 0
  topic_arn = aws_sns_topic.ses_notifications[0].arn
  protocol  = "email"
  endpoint  = var.ses_email_notifications[count.index]
}

# SES identity policy
resource "aws_ses_identity_policy" "ses_policy" {
  count    = var.cognito_ses_authentication ? 1 : 0
  name     = "${var.resource-name-prefix}_ses_policy"
  identity = aws_ses_domain_identity.ses_domain[0].arn
  policy   = data.aws_iam_policy_document.ses_policy_document[0].json
}

data "aws_iam_policy_document" "ses_policy_document" {
  count = var.cognito_ses_authentication ? 1 : 0
  statement {
    effect    = "Deny"
    actions   = ["SES:SendEmail", "SES:SendRawEmail"]
    resources = [aws_ses_domain_identity.ses_domain[0].arn]

    principals {
      type        = "AWS"
      identifiers = [var.aws_account]
    }

    condition {
      test     = "ForAllValues:StringNotEqualsIgnoreCase"
      values   = var.ses_allowed_from_emails
      variable = "ses:FromAddress"
    }
  }
  statement {
    effect    = "Deny"
    actions   = ["SES:SendEmail", "SES:SendRawEmail"]
    resources = [aws_ses_domain_identity.ses_domain[0].arn]

    principals {
      type        = "AWS"
      identifiers = [var.aws_account]
    }

    condition {
      test     = "ForAllValues:StringNotLike"
      values   = [for key in local.allowed_email_domains : "*@${key}"]
      variable = "ses:Recipients"
    }
  }
}

resource "aws_ses_identity_policy" "ses_policy_cognito" {
  count    = var.cognito_ses_authentication ? 1 : 0
  name     = "${var.resource-name-prefix}_ses_policy_cognito"
  identity = aws_ses_domain_identity.ses_domain[0].arn
  policy   = data.aws_iam_policy_document.ses_policy_document_cognito[0].json
}

data "aws_iam_policy_document" "ses_policy_document_cognito" {
  count = var.cognito_ses_authentication ? 1 : 0
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["email.cognito-idp.amazonaws.com"]
    }
    actions   = ["SES:SendEmail", "SES:SendRawEmail"]
    resources = [aws_ses_domain_identity.ses_domain[0].arn]
    condition {
      test     = "StringEquals"
      values   = [var.aws_account]
      variable = "aws:SourceAccount"
    }
    condition {
      test     = "StringEqualsIgnoreCase"
      values   = ["no-reply@${var.domain_name}"]
      variable = "ses:FromAddress"
    }
    condition {
      test     = "StringLike"
      values   = [for key in local.allowed_email_domains : "*@${key}"]
      variable = "ses:Recipients"
    }
  }
}