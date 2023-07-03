variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
}

variable "data_bucket_name" {
  type        = string
  description = "The name of the s3 bucket that ingests the data"
}

variable "log_bucket_name" {
  type        = string
  description = "The name of the S3 bucket to send logs to"
}
