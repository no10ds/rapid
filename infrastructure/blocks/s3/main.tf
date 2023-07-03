terraform {
  backend "s3" {
    key = "s3/terraform.tfstate"
  }
}

resource "aws_s3_bucket" "rapid_data_storage" {
  #checkov:skip=CKV_AWS_144:No need for cross region replication
  #checkov:skip=CKV_AWS_145:No need for non default key

  bucket        = var.data_bucket_name
  acl           = "private"
  force_destroy = false

  tags = var.tags
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "" # use default
        sse_algorithm     = "AES256"
      }
    }
  }
  versioning {
    enabled = true
  }
  logging {
    target_bucket = aws_s3_bucket.logs.bucket
    target_prefix = "log/${var.data_bucket_name}"
  }
}

resource "aws_s3_bucket_public_access_block" "rapid_data_storage" {
  bucket                  = aws_s3_bucket.rapid_data_storage.id
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
  bucket        = var.log_bucket_name
  acl           = "private"
  force_destroy = false

  tags = var.tags
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "" # use default
        sse_algorithm     = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  ignore_public_acls      = true
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}
