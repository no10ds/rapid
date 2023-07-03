resource "random_string" "bucket_id" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket" "rapid_ui" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key
  #checkov:skip=CKV_AWS_19:No need for securely encrypted at rest
  #checkov:skip=CKV2_AWS_6:No need for public access block
  bucket        = "${var.resource-name-prefix}-static-ui-${random_string.bucket_id.result}"
  force_destroy = true
  tags          = var.tags

  versioning {
    enabled = true
  }

  logging {
    target_bucket = var.log_bucket_name
    target_prefix = "log/ui-f1-registry"
  }
}

# Resource to avoid error "AccessControlListNotSupported: The bucket does not allow ACLs"
resource "aws_s3_bucket_ownership_controls" "rapid_ui" {
  bucket = aws_s3_bucket.rapid_ui.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "rapid_ui_storage_acl" {
  bucket     = aws_s3_bucket.rapid_ui.id
  acl        = "private"
  depends_on = [aws_s3_bucket_ownership_controls.rapid_ui]
}

resource "aws_s3_bucket_website_configuration" "rapid_ui_website" {
  bucket = aws_s3_bucket.rapid_ui.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}

locals {
  ui_registry_url = "https://github.com/no10ds/rapid-ui/releases/download/${var.ui_version}"
}

resource "null_resource" "download_static_ui" {
  depends_on = [
    aws_s3_bucket.rapid_ui
  ]

  triggers = {
    ui_version = var.ui_version
    bucket     = aws_s3_bucket.rapid_ui.id
  }

  provisioner "local-exec" {
    command = templatefile("${path.module}/scripts/ui.sh.tpl", {
      REGISTRY_URL = local.ui_registry_url,
      VERSION      = var.ui_version,
      BUCKET_ID    = aws_s3_bucket.rapid_ui.id
    })
  }
}

data "aws_iam_policy_document" "s3" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion"
    ]

    resources = [
      "${aws_s3_bucket.rapid_ui.arn}",
      "${aws_s3_bucket.rapid_ui.arn}/*"
    ]

    principals {
      type = "AWS"
      identifiers = [
        aws_cloudfront_origin_access_identity.rapid_ui.iam_arn
      ]
    }
  }

  statement {
    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.rapid_ui.arn
    ]

    principals {
      type = "AWS"
      identifiers = [
        aws_cloudfront_origin_access_identity.rapid_ui.iam_arn
      ]
    }
  }
}

resource "aws_s3_bucket_policy" "s3" {
  bucket = aws_s3_bucket.rapid_ui.id
  policy = data.aws_iam_policy_document.s3.json
}
