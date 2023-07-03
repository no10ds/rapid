provider "aws" {
  alias  = "us_east"
  region = "us-east-1"

  default_tags {
    tags = var.tags
  }
}

resource "aws_wafv2_web_acl" "rapid_acl" {
  #checkov:skip=CKV2_AWS_31:Already have a logging configuration
  name     = "${var.resource-name-prefix}-acl"
  scope    = "CLOUDFRONT"
  provider = aws.us_east

  default_action {
    block {}
  }

  rule {
    name     = "validate-request"
    priority = 0

    action {
      allow {}
    }

    statement {
      and_statement {
        statement {
          byte_match_statement {
            positional_constraint = "EXACTLY"
            search_string         = var.domain_name
            field_to_match {
              single_header {
                name = "host"
              }
            }
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }

        statement {
          ip_set_reference_statement {
            arn = aws_wafv2_ip_set.this.arn
          }
        }

        statement {
          not_statement {
            statement {
              sqli_match_statement {
                field_to_match {
                  body {
                    oversize_handling = "CONTINUE"
                  }
                }
                text_transformation {
                  priority = 0
                  type     = "NONE"
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "validate-request"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "validate-query"
    priority = 1

    action {
      block {}
    }

    statement {
      and_statement {
        statement {
          byte_match_statement {
            positional_constraint = "ENDS_WITH"

            search_string = "/query"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }
        statement {
          not_statement {
            statement {
              size_constraint_statement {
                comparison_operator = "GT"
                size                = "8192"
                field_to_match {
                  body {
                    oversize_handling = "CONTINUE"
                  }
                }
                text_transformation {
                  priority = 0
                  type     = "NONE"
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "validate-request"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "validate-large-query"
    priority = 2

    action {
      block {}
    }

    statement {
      and_statement {
        statement {
          byte_match_statement {
            positional_constraint = "ENDS_WITH"

            search_string = "/query/large"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }
        statement {
          not_statement {
            statement {
              size_constraint_statement {
                comparison_operator = "GT"
                size                = "8192"
                field_to_match {
                  body {
                    oversize_handling = "CONTINUE"
                  }
                }
                text_transformation {
                  priority = 0
                  type     = "NONE"
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "validate-request"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "aws-known-bad-input"
      sampled_requests_enabled   = true
    }
  }


  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.resource-name-prefix}-acl"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_ip_set" "this" {
  provider           = aws.us_east
  name               = "${var.resource-name-prefix}-ip_set"
  description        = "Whitelisted IPs that can access Cloudfront"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = var.ip_whitelist
}
