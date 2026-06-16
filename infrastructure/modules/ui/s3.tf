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
  #checkov:skip=CKV2_AWS_62:No need for event notifications
  #checkov:skip=CKV2_AWS_61:No need for lifecycle configuration
  bucket        = "${var.resource-name-prefix}-static-ui-${random_string.bucket_id.result}"
  force_destroy = true
  tags          = var.tags

}

resource "aws_s3_bucket_versioning" "rapid_ui" {
  bucket = aws_s3_bucket.rapid_ui.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_logging" "rapid_ui" {
  bucket = aws_s3_bucket.rapid_ui.id

  target_bucket = var.log_bucket_name
  target_prefix = "log/ui-f1-registry"
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

data "github_release" "this" {
  repository  = "rapid"
  owner       = "no10ds"
  retrieve_by = "tag"
  release_tag = var.ui_version
}

data "github_release_asset" "router_lambda" {
  repository    = "rapid"
  owner         = "no10ds"
  asset_id      = data.github_release.this.assets[index(data.github_release.this.assets.*.name, "${var.ui_version}-router-lambda.zip")]
  download_file = true
}

resource "local_file" "router_lambda" {
  content_base64 = github_release_asset.router_lambda.file_contents
  filename       = "${var.ui_version}-router-lambda.zip"
}

data "github_release_asset" "static_ui" {
  repository    = "rapid"
  owner         = "no10ds"
  asset_id      = data.github_release.this.assets[index(data.github_release.this.assets.*.name, "${var.ui_version}.zip")]
  download_file = true
}

resource "local_file" "static_ui" {
  content_base64 = github_release_asset.static_ui.file_contents
  filename       = "${var.ui_version}.zip"
}

resource "terraform_data" "static_ui" {
  input = {
    version = var.ui_version,
    bucket  = aws_s3_bucket.rapid_ui.id
  }

  triggers_replace = [
    var.ui_version,
    aws_s3_bucket.rapid_ui.id
  ]

  provisioner "local-exec" {
    interpreter = local.interpreter

    command = <<-EOT
    unzip -o "${var.ui_version}.zip"
    EOT

  }

}

resource "aws_s3_object" "static_ui" {
  for_each = fileset("out", "**")

  key    = each.value
  bucket = aws_s3_bucket.rapid_ui.id
  source = "out/${each.value}"
  etag   = filemd5("out/${each.value}")

  lifecycle {
    ignore_changes = [
      source, etag
    ]
    replace_triggered_by = [
      terraform_data.static_ui.output.version,
      terraform_data.static_ui.output.bucket
    ]
  }
}

/*
locals {
  ui_registry_url = "https://github.com/no10ds/rapid/releases/download/${var.ui_version}"
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
*/

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
