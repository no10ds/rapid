resource "aws_iam_policy" "pipeline_ecr_access" {
  name        = "pipeline_ecr_access"
  description = "Allow pipeline to access ECR"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Effect : "Allow",
        Action : [
          "ecr:GetAuthorizationToken",
        ],
        Resource : "*"
      },
      {
        Effect : "Allow",
        Action : [
          "ecs:UpdateService",
          "ecs:DescribeServices",
        ],
        Resource : "arn:aws:ecs:${var.aws_region}:${var.aws_account}:*"
      },
      {
        Effect : "Allow",
        Action : [
          "ecr:BatchDeleteImage",
          "ecr:DescribeImageScanFindings",
          "ecr:GetDownloadUrlForLayer",
          "ecr:DescribeRegistry",
          "ecr:DescribeImageReplicationStatus",
          "ecr:GetAuthorizationToken",
          "ecr:ListTagsForResource",
          "ecr:UploadLayerPart",
          "ecr:ListImages",
          "ecr:PutImage",
          "ecr:UntagResource",
          "ecr:BatchGetImage",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeImages",
          "ecr:TagResource",
          "ecr:DescribeRepositories",
          "ecr:InitiateLayerUpload",
          "ecr:BatchCheckLayerAvailability",
        ],
        Resource : [
          data.terraform_remote_state.ecr-state.outputs.ecr_private_repo_arn,
          data.terraform_remote_state.ecr-state.outputs.ecr_private_ckan_repo_arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "pipeline_ecr_public_access" {
  name        = "pipeline_ecr_public_access"
  description = "Allow pipeline to access the public ECR"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Effect : "Allow",
        Action : [
          "ecr-public:GetAuthorizationToken",
          "sts:GetServiceBearerToken",
        ],
        Resource : "*"
      },
      {
        Effect : "Allow",
        Action : [
          "ecr-public:BatchCheckLayerAvailability",
          "ecr-public:GetRepositoryPolicy",
          "ecr-public:DescribeRepositories",
          "ecr-public:DescribeRegistries",
          "ecr-public:DescribeImages",
          "ecr-public:DescribeImageTags",
          "ecr-public:GetRepositoryCatalogData",
          "ecr-public:GetRegistryCatalogData",
          "ecr-public:InitiateLayerUpload",
          "ecr-public:UploadLayerPart",
          "ecr-public:CompleteLayerUpload",
          "ecr-public:PutImage"
        ],
        Resource : [
          data.terraform_remote_state.ecr-state.outputs.ecr_public_repo_arn,
          data.terraform_remote_state.ecr-state.outputs.ecr_public_ckan_repo_arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "pipeline_s3_access" {
  name        = "pipeline_s3_access"
  description = "Allow pipeline to access S3"
  tags        = var.tags

  policy = jsonencode({
    "Statement" : [
      {
        "Action" : "s3:ListBucket",
        "Effect" : "Allow",
        "Resource" : [
          data.terraform_remote_state.s3-state.outputs.s3_bucket_arn
        ]
      },
      {
        "Action" : [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:DeleteObjects",
          "s3:ListObjects"
        ],
        "Effect" : "Allow",
        "Resource" : [
          "${data.terraform_remote_state.s3-state.outputs.s3_bucket_arn}/data/test_e2e/*",
          "${data.terraform_remote_state.s3-state.outputs.s3_bucket_arn}/data/schemas/PUBLIC/test_e2e/*",
          "${data.terraform_remote_state.s3-state.outputs.s3_bucket_arn}/raw_data/test_e2e/*"
        ]
      }
    ],
    "Version" : "2012-10-17"
  })
}

resource "aws_iam_policy" "pipeline_secrets_manager_access" {
  name        = "pipeline_secrets_manager_access"
  description = "Allow pipeline to access AWS Secrets Manager"
  tags        = var.tags

  policy = jsonencode({
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "secretsmanager:GetRandomPassword",
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:ListSecrets"
        ],
        "Resource" : "*"
      }
    ],
    "Version" : "2012-10-17"
  })
}

resource "aws_iam_policy" "pipeline_ssm_access" {
  name        = "pipeline_ssm_access"
  description = "Allow pipeline to use SSM"
  tags        = var.tags

  policy = jsonencode({
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "ssm:UpdateInstanceInformation",
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ],
        "Resource" : "*"
      }
    ],
    "Version" : "2012-10-17"
  })
}

resource "aws_iam_policy" "pipeline_dynamodb_access" {
  name        = "pipeline_dynamodb_access"
  description = "Allow pipeline to access DynamoDB"
  tags        = var.tags

  policy = jsonencode({
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:Query",
          "dynamodb:BatchWriteItem",
        ],
        "Resource" : "*"
      }
    ],
    "Version" : "2012-10-17"
  })
}

resource "aws_iam_policy" "pipeline_glue_access" {
  name        = "pipeline_glue_access"
  description = "Allow pipeline to access Glue"
  tags        = var.tags

  policy = jsonencode({
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "glue:DeleteTable",
          "glue:TagResource",
        ],
        "Resource" : "*"
      },
    ],
    "Version" : "2012-10-17"
  })
}

resource "aws_iam_role" "pipeline_ecr_role" {
  name = "pipeline-ecr-role"
  tags = var.tags

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ssm_role_policy_attach" {
  role       = aws_iam_role.pipeline_ecr_role.name
  policy_arn = aws_iam_policy.pipeline_ssm_access.arn
}

resource "aws_iam_role_policy_attachment" "ecr_role_policy_attach" {
  role       = aws_iam_role.pipeline_ecr_role.name
  policy_arn = aws_iam_policy.pipeline_ecr_access.arn
}

resource "aws_iam_role_policy_attachment" "ecr_public_role_policy_attach" {
  role       = aws_iam_role.pipeline_ecr_role.name
  policy_arn = aws_iam_policy.pipeline_ecr_public_access.arn
}

resource "aws_iam_role_policy_attachment" "s3_role_policy_attach" {
  role       = aws_iam_role.pipeline_ecr_role.name
  policy_arn = aws_iam_policy.pipeline_s3_access.arn
}

resource "aws_iam_role_policy_attachment" "secrets_manager_role_policy_attach" {
  role       = aws_iam_role.pipeline_ecr_role.name
  policy_arn = aws_iam_policy.pipeline_secrets_manager_access.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_role_policy_attach" {
  role       = aws_iam_role.pipeline_ecr_role.name
  policy_arn = aws_iam_policy.pipeline_dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "glue_role_policy_attach" {
  role       = aws_iam_role.pipeline_ecr_role.name
  policy_arn = aws_iam_policy.pipeline_glue_access.arn
}
