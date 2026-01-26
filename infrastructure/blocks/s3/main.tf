terraform {
  backend "s3" {
    key = "s3/terraform.tfstate"
  }
}

resource "aws_s3_bucket" "rapid_data_storage" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key
  #checkov:skip=CKV2_AWS_62:No need for event notifications
  #checkov:skip=CKV2_AWS_61:No need for lifecycle configuration
  bucket        = var.data_bucket_name
  force_destroy = false

  tags = var.tags
}

resource "aws_s3_bucket_server_side_encryption_configuration" "rapid_data_storage" {
  bucket = aws_s3_bucket.rapid_data_storage.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = "" # use default
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "rapid_data_storage" {
  bucket = aws_s3_bucket.rapid_data_storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_logging" "rapid_data_storage" {
  bucket = aws_s3_bucket.rapid_data_storage.id

  target_bucket = aws_s3_bucket.logs.bucket
  target_prefix = "log/${var.data_bucket_name}"
}

resource "aws_s3_bucket_ownership_controls" "rapid_data_storage" {
  bucket = aws_s3_bucket.rapid_data_storage.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "rapid_data_storage" {
  depends_on = [aws_s3_bucket_ownership_controls.rapid_data_storage]
  bucket     = aws_s3_bucket.rapid_data_storage.id
  acl        = "private"
}

resource "aws_s3_bucket_public_access_block" "rapid_data_storage" {
  bucket                  = aws_s3_bucket.rapid_data_storage.id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_notification" "rapid_data_storage" {
  bucket      = aws_s3_bucket.rapid_data_storage.id
  eventbridge = true
}

resource "aws_s3_bucket" "logs" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key
  #checkov:skip=CKV_AWS_18:Log bucket shouldn't be logging
  #checkov:skip=CKV_AWS_21:No need to version log bucket
  #checkov:skip=CKV2_AWS_62:No need for event notifications
  #checkov:skip=CKV2_AWS_61:No need for lifecycle configuration
  bucket        = var.log_bucket_name
  force_destroy = false

  tags = var.tags
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

resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "logs" {
  depends_on = [aws_s3_bucket_ownership_controls.logs]
  bucket     = aws_s3_bucket.logs.id
  acl        = "private"
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}
