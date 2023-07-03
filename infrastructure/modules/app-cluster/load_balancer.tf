resource "aws_alb" "application_load_balancer" {
  #checkov:skip=CKV_AWS_150:No need for deletion protection
  #checkov:skip=CKV2_AWS_28:No need for load balancer waf
  name                       = "${var.resource-name-prefix}-alb"
  internal                   = false
  load_balancer_type         = "application"
  subnets                    = var.public_subnet_ids_list
  security_groups            = [aws_security_group.load_balancer_security_group.id]
  drop_invalid_header_fields = true
  enable_deletion_protection = true

  access_logs {
    bucket  = var.log_bucket_name
    prefix  = "${var.resource-name-prefix}-alb"
    enabled = true
  }

  tags = var.tags
}

data "aws_elb_service_account" "main" {}

resource "aws_s3_bucket_policy" "allow_alb_logging" {
  bucket = var.log_bucket_name
  policy = <<POLICY
{
  "Id": "Policy",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSLogDeliveryWrite",
      "Effect": "Allow",
      "Principal": {
        "AWS": "${data.aws_elb_service_account.main.arn}"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${var.log_bucket_name}/${var.resource-name-prefix}-alb/AWSLogs/${var.aws_account}/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    },
    {
      "Sid": "AllowSSLRequestsOnly",
      "Action": "s3:*",
      "Effect": "Deny",
      "Resource": [
        "arn:aws:s3:::${var.log_bucket_name}/*",
        "arn:aws:s3:::${var.log_bucket_name}"
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

data "aws_ec2_managed_prefix_list" "cloudwatch" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}
resource "aws_security_group" "load_balancer_security_group" {
  vpc_id      = var.vpc_id
  description = "ALB Security Group"
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudwatch.id]
    description     = "Allow HTTP ingress"
  }
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudwatch.id]
    description     = "Allow HTTPS ingress"
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
    description      = "Allow all egress"
  }
  tags = var.tags
}

resource "aws_lb_target_group" "target_group" {
  name        = "${var.resource-name-prefix}-tg"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    healthy_threshold   = 3
    interval            = 300
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = 3
    path                = "/api/status"
    unhealthy_threshold = 2
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = var.tags
}

resource "aws_lb_listener" "listener" {
  # checkov:skip=CKV2_AWS_28:ALB access is limited to cloudfront which has WAF enabled
  load_balancer_arn = aws_alb.application_load_balancer.id
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = var.certificate_validation_arn != "" ? var.certificate_validation_arn : aws_acm_certificate_validation.rapid-certificate-validation[0].certificate_arn
  tags              = var.tags
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.id
  }
}

resource "aws_lb_listener" "http-listener" {
  load_balancer_arn = aws_alb.application_load_balancer.id
  port              = "80"
  protocol          = "HTTP"
  tags              = var.tags

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
