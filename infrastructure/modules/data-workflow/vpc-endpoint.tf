resource "aws_vpc_endpoint" "s3_vpc_endpoint" {
  vpc_id       = var.vpc_id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  tags = var.tags
}

resource "aws_security_group" "glue_connection_sg" {
  #checkov:skip=CKV2_AWS_5:SG is attached
  name        = "${var.resource-name-prefix}-glue_connection_sg"
  description = "Allow crawler to read s3 bucket"
  vpc_id      = var.vpc_id
  ingress {
    description     = "Allow HTTPS from S3 VPC Endpoint"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [data.aws_prefix_list.s3_prefix.prefix_list_id]
  }

  ingress {
    description = "Allow all internal traffic"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }

  egress {
    description      = "Allow all egress"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = var.tags
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_prefix_list" "s3_prefix" {
  prefix_list_id = aws_vpc_endpoint.s3_vpc_endpoint.prefix_list_id
}
