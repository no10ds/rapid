resource "aws_glue_catalog_database" "catalogue_db" {
  name = "${var.resource-name-prefix}_catalogue_db"
}

resource "aws_glue_connection" "glue_connection" {
  name            = "${var.resource-name-prefix}-s3-network-connection"
  connection_type = "NETWORK"

  physical_connection_requirements {
    availability_zone      = data.aws_availability_zones.available.names[0]
    security_group_id_list = [aws_security_group.glue_connection_sg.id]
    subnet_id              = var.private_subnet
  }
}

resource "aws_glue_catalog_table" "metadata" {
  name          = "${var.resource-name-prefix}_metadata_table"
  database_name = aws_glue_catalog_database.catalogue_db.name

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "EXTERNAL" = "TRUE"
  }

  storage_descriptor {
    location      = "s3://${var.data_s3_bucket_name}/data/schemas"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat"

    columns {
      name = "metadata"
      type = "struct<dataset:string,domain:string,sensitivity:string,version:string,description:string,key_value_tags:string,key_only_tags:string,owners:array<struct<name:string,email:string>>,update_behaviour:string>"
    }

    columns {
      name    = "columns"
      type    = "array<struct<name:string,partition_index:int,data_type:string,allow_null:boolean,format:string>>"
      comment = ""
    }

    ser_de_info {
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }
  }
}

resource "aws_iam_role" "glue_service_role" {
  name        = "${var.resource-name-prefix}-glue_services_access"
  description = "Allow AWS Glue service to access S3 via crawler"
  tags        = var.tags

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "crawler_s3_policy" {
  name        = "${var.resource-name-prefix}-crawler_data_access_policy"
  description = "Allow crawler to access data in s3 bucket"
  tags        = var.tags

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "${var.data_s3_bucket_arn}/data/*"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "glue_service_role_s3_policy_attach" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = aws_iam_policy.crawler_s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "glue_service_role_managed_policy_attach" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_cloudwatch_log_group" "aws_glue_crawlers_log_group" {
  #checkov:skip=CKV_AWS_158:No need for KMS
  name              = "/${var.resource-name-prefix}-aws-glue/crawlers"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "aws_glue_connection_error_log_group" {
  #checkov:skip=CKV_AWS_158:No need for KMS
  name              = "/${var.resource-name-prefix}-aws-glue/testconnection/error/s3-network-connection"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "aws_glue_connection_log_group" {
  #checkov:skip=CKV_AWS_158:No need for KMS
  name              = "/${var.resource-name-prefix}-aws-glue/testconnection/output/s3-network-connection"
  retention_in_days = 90
}
