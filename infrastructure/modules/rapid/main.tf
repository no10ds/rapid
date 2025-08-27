module "app_cluster" {
  source                                          = "../app-cluster"
  app-replica-count-desired                       = var.app-replica-count-desired
  app-replica-count-max                           = var.app-replica-count-max
  resource-name-prefix                            = var.resource-name-prefix
  application_version                             = var.application_version
  support_emails_for_cloudwatch_alerts            = var.support_emails_for_cloudwatch_alerts
  cognito_user_login_app_credentials_secrets_name = module.auth.cognito_user_app_secret_manager_name
  cognito_user_pool_id                            = module.auth.cognito_user_pool_id
  permissions_table_arn                           = module.auth.user_permission_table_arn
  schema_table_arn                                = module.data_workflow.schema_table_arn
  catalogue_db_name                               = module.data_workflow.catalogue_db_name
  layers                                          = var.layers
  domain_name                                     = var.domain_name
  allowed_email_domains                           = var.allowed_email_domains
  rapid_ecr_url                                   = var.rapid_ecr_url
  certificate_validation_arn                      = var.certificate_validation_arn
  hosted_zone_id                                  = var.hosted_zone_id
  aws_account                                     = var.aws_account
  aws_region                                      = var.aws_region
  data_s3_bucket_arn                              = aws_s3_bucket.this.arn
  data_s3_bucket_name                             = aws_s3_bucket.this.id
  log_bucket_name                                 = aws_s3_bucket.logs.id
  catalog_disabled                                = var.catalog_disabled
  vpc_id                                          = var.vpc_id
  public_subnet_ids_list                          = var.public_subnet_ids_list
  private_subnet_ids_list                         = var.private_subnet_ids_list
  athena_query_output_bucket_arn                  = module.data_workflow.athena_query_result_output_bucket_arn
  ip_whitelist                                    = var.ip_whitelist
  enable_cloudtrail                               = var.enable_cloudtrail
  ecs_cluster_arn                                 = var.ecs_cluster_arn
  ecs_cluster_name                                = var.ecs_cluster_name
  ecs_cluster_id                                  = var.ecs_cluster_id
  custom_user_name_regex                          = var.custom_user_name_regex
  task_cpu                                        = var.task_cpu
  task_memory                                     = var.task_memory
}

module "auth" {
  source               = "../auth"
  tags                 = var.tags
  domain_name          = var.domain_name
  resource-name-prefix = var.resource-name-prefix
  password_policy      = var.password_policy
  layers               = var.layers
  ses_arn              = var.ses_service ? module.ses.ses_arn[0] : null
}

module "data_workflow" {
  source               = "../data-workflow"
  resource-name-prefix = var.resource-name-prefix
  aws_account          = var.aws_account
  aws_region           = var.aws_region
}

module "ui" {
  source                             = "../ui"
  tags                               = var.tags
  log_bucket_name                    = aws_s3_bucket.logs.id
  us_east_certificate_validation_arn = var.us_east_certificate_validation_arn
  domain_name                        = var.domain_name
  hosted_zone_id                     = var.hosted_zone_id != "" ? var.hosted_zone_id : module.app_cluster.hosted_zone_id
  ip_whitelist                       = var.ip_whitelist
  resource-name-prefix               = var.resource-name-prefix
  aws_account                        = var.aws_account
  ui_version                         = var.ui_version
  load_balancer_dns                  = module.app_cluster.load_balancer_dns
  route_53_validation_record_fqdns   = module.app_cluster.route_53_validation_record_fqdns
  geo_restriction_locations          = var.geo_restriction_locations
  sql_injection_protection           = var.sql_injection_protection
}

module "ses" {
  source = "../ses"

  ses_service                              = var.ses_service
  resource-name-prefix                     = var.resource-name-prefix
  aws_account                              = var.aws_account
  aws_region                               = var.aws_region
  tags                                     = var.tags
  domain_name                              = var.domain_name
  hosted_zone_id                           = var.hosted_zone_id != "" ? var.hosted_zone_id : module.app_cluster.hosted_zone_id
  ses_support_emails_for_cloudwatch_alerts = var.ses_support_emails_for_cloudwatch_alerts
  allowed_sender_email_addresses           = var.allowed_sender_email_addresses
  allowed_recipients_email_domains         = var.allowed_email_domains
}

resource "aws_s3_bucket" "this" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key
  #checkov:skip=CKV2_AWS_62:No need for event notifications
  #checkov:skip=CKV2_AWS_61:No need for lifecycle configuration

  bucket        = var.resource-name-prefix
  force_destroy = false

  tags = var.tags

}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = "" # use default
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_logging" "this" {
  bucket = aws_s3_bucket.this.id

  target_bucket = aws_s3_bucket.logs.bucket
  target_prefix = "log/${var.resource-name-prefix}"
}

resource "aws_s3_bucket_notification" "this" {
  bucket      = aws_s3_bucket.this.id
  eventbridge = true
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "logs" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key
  #checkov:skip=CKV_AWS_18:Log bucket shouldn't be logging
  #checkov:skip=CKV_AWS_21:No need to version log bucket
  #checkov:skip=CKV2_AWS_62:No need for event notifications
  #checkov:skip=CKV2_AWS_61:No need for lifecycle configuration
  bucket        = "${var.resource-name-prefix}-logs"
  force_destroy = false

  tags = var.tags
}

resource "aws_s3_bucket_acl" "logs" {
  bucket = aws_s3_bucket.logs.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = "" # use default
      sse_algorithm     = "AES256"
    }
  }
}

# Resource to avoid error "AccessControlListNotSupported: The bucket does not allow ACLs"
resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  depends_on              = [aws_s3_bucket_ownership_controls.logs]
}

resource "aws_s3_bucket_policy" "log_bucket_policy" {
  bucket = aws_s3_bucket.this.id
  policy = <<POLICY
    {
        "Version": "2012-10-17",
        "Statement": [
            {
              "Sid": "AllowSSLRequestsOnly",
              "Action": "s3:*",
              "Effect": "Deny",
              "Resource": [
                "${aws_s3_bucket.this.arn}/*",
                "${aws_s3_bucket.this.arn}"
              ],
              "Condition": {
                "Bool": {
                  "aws:SecureTransport": "false"
                }
             },
              "Principal": "*"
           }
        ]
    }
POLICY
}
