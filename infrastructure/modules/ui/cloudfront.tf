resource "aws_cloudfront_origin_access_identity" "rapid_ui" {}

resource "random_string" "random_cloudfront_header" {
  length           = 16
  special          = true
  override_special = "/@£$"
}
data "aws_cloudfront_cache_policy" "optimised" {
  name = "Managed-CachingDisabled"
}

resource "aws_cloudfront_cache_policy" "rapid_ui_lb" {
  name        = "${var.resource-name-prefix}-api-lb-cache-policy"
  min_ttl     = 1
  max_ttl     = 1
  default_ttl = 1

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }

    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Authorization"]
      }
    }

    query_strings_config {
      query_string_behavior = "none"
    }
  }

}

resource "aws_cloudfront_origin_request_policy" "rapid_ui_lb" {
  name = "${var.resource-name-prefix}-api-lb-request-policy"

  cookies_config {
    cookie_behavior = "all"
  }

  headers_config {
    header_behavior = "whitelist"
    headers {
      items = ["Host", "Accept", "Origin", "Referer"]
    }
  }

  query_strings_config {
    query_string_behavior = "all"
  }
}

resource "aws_cloudfront_distribution" "rapid_ui" {
  # checkov:skip=CKV2_AWS_32: No need for strict security headers
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  aliases             = ["${var.domain_name}"]
  web_acl_id          = aws_wafv2_web_acl.rapid_acl.arn

  depends_on = [
    random_string.bucket_id,
    aws_s3_bucket.rapid_ui,
  ]

  viewer_certificate {
    acm_certificate_arn      = local.domain_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  origin {
    domain_name = aws_s3_bucket.rapid_ui.bucket_regional_domain_name
    origin_id   = "${var.resource-name-prefix}-ui-origin"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.rapid_ui.cloudfront_access_identity_path
    }
  }

  origin {
    domain_name = var.load_balancer_dns
    origin_id   = "${var.resource-name-prefix}-api-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "match-viewer"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = var.geo_restriction_locations
    }
  }

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "${var.resource-name-prefix}-ui-origin"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    lambda_function_association {
      event_type   = "origin-request"
      lambda_arn   = aws_lambda_function.this.qualified_arn
      include_body = false
    }
  }

  ordered_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["HEAD", "GET"]
    target_origin_id       = "${var.resource-name-prefix}-api-origin"
    viewer_protocol_policy = "redirect-to-https"
    path_pattern           = "/api/*"

    cache_policy_id          = aws_cloudfront_cache_policy.rapid_ui_lb.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.rapid_ui_lb.id
  }

  logging_config {
    bucket          = "${var.log_bucket_name}.s3.amazonaws.com"
    prefix          = "${var.resource-name-prefix}-cloudfront"
    include_cookies = true
  }
}

resource "aws_route53_record" "route-to-cloudfront" {
  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.rapid_ui.domain_name
    zone_id                = aws_cloudfront_distribution.rapid_ui.hosted_zone_id
    evaluate_target_health = false
  }
}

locals {
  domain_certificate_arn    = var.us_east_certificate_validation_arn == "" ? aws_acm_certificate.rapid_certificate[0].arn : var.us_east_certificate_validation_arn
  domain_validation_options = var.us_east_certificate_validation_arn == "" ? aws_acm_certificate.rapid_certificate[0].domain_validation_options : []
}

resource "aws_route53_record" "rapid_validation_record" {
  for_each = {
    for dvo in local.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
    if length(var.route_53_validation_record_fqdns) == 0
  }

  zone_id = var.hosted_zone_id
  name    = each.value.name
  records = [each.value.record]
  type    = each.value.type
  ttl     = 60
}


resource "aws_acm_certificate" "rapid_certificate" {
  provider          = aws.us_east
  count             = var.us_east_certificate_validation_arn == "" ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "rapid_certificate" {
  provider                = aws.us_east
  count                   = var.us_east_certificate_validation_arn == "" ? 1 : 0
  certificate_arn         = aws_acm_certificate.rapid_certificate[0].arn
  validation_record_fqdns = length(var.route_53_validation_record_fqdns) == 0 ? [for record in aws_route53_record.rapid_validation_record : record.fqdn] : var.route_53_validation_record_fqdns
}
