resource "aws_iam_role" "this" {
  name = "${var.resource-name-prefix}-cloudfront-router-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = [
            "lambda.amazonaws.com",
            "edgelambda.amazonaws.com"
          ]
        }
      }
    ]
  })
}

data "aws_iam_policy_document" "this" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "cloudfront_router_policy" {
  name        = "${var.resource-name-prefix}-cloudfront-router-policy"
  description = "Managed policy for CloudFront Lambda@Edge router logging"
  policy      = data.aws_iam_policy_document.this.json
}

resource "aws_iam_role_policy_attachment" "cloudfront_router_policy_attachment" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.cloudfront_router_policy.arn
}

resource "aws_lambda_function" "this" {
  #checkov:skip=CKV_AWS_116:No need for lambda dead letter queue
  #checkov:skip=CKV_AWS_117:No need for vpc
  #checkov:skip=CKV_AWS_272:No need for lambda code-signing validation
  provider                       = aws.us_east
  function_name                  = "${var.resource-name-prefix}-cloudfront-router"
  role                           = aws_iam_role.this.arn
  filename                       = "${path.root}/${var.ui_version}-router-lambda.zip"
  reserved_concurrent_executions = 25
  tracing_config {
    mode = "Active"
  }

  runtime = "nodejs20.x"
  handler = "lambda/lambda.handler"

  publish = true

  depends_on = [
    null_resource.download_static_ui
  ]
}
