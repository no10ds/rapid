locals {
  environment_variables = merge({
    "AWS_ACCOUNT" : var.aws_account,
    "DATA_BUCKET" : var.data_s3_bucket_name,
    "DOMAIN_NAME" : var.domain_name,
    "CATALOG_DISABLED" : tostring(var.catalog_disabled),
    "ALLOWED_EMAIL_DOMAINS" : var.allowed_email_domains,
    "COGNITO_USER_POOL_ID" : var.cognito_user_pool_id,
    "RESOURCE_PREFIX" : var.resource-name-prefix,
    "COGNITO_USER_LOGIN_APP_CREDENTIALS_SECRETS_NAME" : var.cognito_user_login_app_credentials_secrets_name
  }, var.project_information)
}

resource "aws_iam_role" "ecsTaskExecutionRole" {
  name               = "${var.resource-name-prefix}-ecs-execution-task-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
  tags               = var.tags
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_policy" "app_s3_access" {
  name        = "${var.resource-name-prefix}-app_s3_access"
  description = "Allow application instance to access S3"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Effect : "Allow",
        Action : ["s3:GetObject", "s3:PutObject"],
        Resource : "${var.data_s3_bucket_arn}/*"
      },
      {
        Effect : "Allow",
        Action : ["s3:DeleteObject"],
        Resource : [
          "${var.data_s3_bucket_arn}/*.csv",
          "${var.data_s3_bucket_arn}/*.parquet"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:DeleteObject",
          "s3:GetObject",
          "s3:PutObject"
        ],
        "Resource" : "${var.data_s3_bucket_arn}/data/schemas/**/*.json"
      }
    ]
  })
}

resource "aws_iam_policy" "app_athena_query_access" {
  name        = "${var.resource-name-prefix}-app_query_access"
  description = "Allow application instance to access catalog's db"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "Athena",
        "Effect" : "Allow",
        "Action" : [
          "athena:ListWorkGroups",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:GetWorkGroup",
          "athena:StartQueryExecution",
          "athena:StopQueryExecution",
        ],
        "Resource" : [
          "arn:aws:athena:${var.aws_region}:${var.aws_account}:workgroup/${var.resource-name-prefix}_athena_workgroup"
        ]
      },
      {
        "Sid" : "DataBucket",
        "Effect" : "Allow",
        "Action" : [
          "s3:ListBucket",
          "s3:GetObject"
        ],
        "Resource" : [
          var.data_s3_bucket_arn
        ]
      },
      {
        "Sid" : "ResultBucket",
        "Effect" : "Allow",
        "Action" : [
          "s3:ListMultipartUploadParts",
          "s3:ListBucket",
          "s3:*Object*",
          "s3:GetBucketLocation",
          "s3:AbortMultipartUpload",
        ],
        "Resource" : [
          var.athena_query_output_bucket_arn,
          "${var.athena_query_output_bucket_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "app_glue_access" {
  name        = "${var.resource-name-prefix}-app_glue_access"
  description = "Allow application instance to access Glue"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartitions",
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:UpdateTable",
          "glue:BatchDeleteTable",
          "glue:CreateTable"
        ],
        "Resource" : [
          "*"
        ]
      },
    ]
  })
}

resource "aws_iam_policy" "app_cognito_access" {
  name        = "${var.resource-name-prefix}-app_cognito_access"
  description = "Allow application instance to access Cognito"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Effect : "Allow",
        Action : [
          "cognito-idp:CreateUserPoolClient",
          "cognito-idp:CreateGroup",
          "cognito-idp:DeleteGroup",
          "cognito-idp:DescribeResourceServer",
          "cognito-idp:AdminCreateUser",
          "cognito-idp:AdminDeleteUser",
          "cognito-idp:AdminGetUser",
          "cognito-idp:ListUsers",
          "cognito-idp:DeleteUserPoolClient",
          "cognito-idp:DescribeUserPoolClient",
          "cognito-idp:ListUserPoolClients",
          "cognito-idp:UpdateResourceServer"
        ],
        Resource : "arn:aws:cognito-idp:${var.aws_region}:${var.aws_account}:userpool/${var.cognito_user_pool_id}"
      }
    ]
  })
}

resource "aws_iam_policy" "app_dynamodb_access" {
  name        = "${var.resource-name-prefix}-app_dynamodb_access"
  description = "Allow application instance to access DynamoDB"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Effect : "Allow",
        Action : [
          "dynamodb:DeleteItem",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem"
        ],
        Resource : [
          var.permissions_table_arn,
          var.schema_table_arn,
          aws_dynamodb_table.service_table.arn,
          "${aws_dynamodb_table.service_table.arn}/index/*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "app_secrets_manager_access" {
  name        = "${var.resource-name-prefix}-app_secrets_manager_access"
  description = "Allow application instance to access AWS Secrets Manager"
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

resource "aws_iam_policy" "app_tags_access" {
  name        = "${var.resource-name-prefix}-app_tags_access"
  description = "Allow application instance to get resources by tags"
  tags        = var.tags

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Effect : "Allow",
        Action : ["tag:GetResources"],
        Resource : "*"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "role_s3_access_policy_attachment" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = aws_iam_policy.app_s3_access.arn
}

resource "aws_iam_role_policy_attachment" "role_cognito_access_policy_attachment" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = aws_iam_policy.app_cognito_access.arn
}

resource "aws_iam_role_policy_attachment" "role_secrets_manager_access_policy_attachment" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = aws_iam_policy.app_secrets_manager_access.arn
}

resource "aws_iam_role_policy_attachment" "role_athena_access_policy_attachment" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = aws_iam_policy.app_athena_query_access.arn
}

resource "aws_iam_role_policy_attachment" "role_glue_access_policy_attachment" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = aws_iam_policy.app_glue_access.arn
}

resource "aws_iam_role_policy_attachment" "role_tags_access_policy_attachment" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = aws_iam_policy.app_tags_access.arn
}

resource "aws_iam_role_policy_attachment" "role_dynamodb_access_policy_attachment" {
  role       = aws_iam_role.ecsTaskExecutionRole.name
  policy_arn = aws_iam_policy.app_dynamodb_access.arn
}

resource "aws_ecs_cluster" "aws-ecs-cluster" {
  name = "${var.resource-name-prefix}-cluster"
  tags = var.tags
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "log-group" {
  #checkov:skip=CKV_AWS_158:No need for KMS
  name              = "${var.resource-name-prefix}-logs"
  tags              = var.tags
  retention_in_days = 90
}

resource "aws_ecs_task_definition" "aws-ecs-task" {
  #checkov:skip=CKV_AWS_249
  family = "${var.resource-name-prefix}-task"

  container_definitions = <<DEFINITION
  [
    {
      "name": "${var.resource-name-prefix}-container",
      "volumesFrom": [],
      "mountPoints": [],
      "image": "${var.rapid_ecr_url}:${var.application_version}",
      "entryPoint": [],
      "essential": true,
      "environment": ${jsonencode([
  for key, value in local.environment_variables :
  {
    "name" : "${upper(key)}",
    "value" : "${value}"
  }
])},
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.log-group.id}",
          "awslogs-region": "${var.aws_region}",
          "awslogs-stream-prefix": "${var.resource-name-prefix}-app-logs"
        }
      },
      "portMappings": [
        {
          "containerPort": ${var.container_port},
          "hostPort": ${var.host_port},
          "protocol": "${var.protocol}"
        }
      ],
      "cpu": 256,
      "memory": 512,
      "networkMode": "awsvpc"
    }
  ]
  DEFINITION

requires_compatibilities = ["FARGATE"]
network_mode             = "awsvpc"
memory                   = "512"
cpu                      = "256"
execution_role_arn       = aws_iam_role.ecsTaskExecutionRole.arn
task_role_arn            = aws_iam_role.ecsTaskExecutionRole.arn

tags = var.tags
}

data "aws_ecs_task_definition" "main" {
  task_definition = aws_ecs_task_definition.aws-ecs-task.family
}

resource "aws_ecs_service" "aws-ecs-service" {
  name                 = "${var.resource-name-prefix}-ecs-service"
  cluster              = aws_ecs_cluster.aws-ecs-cluster.id
  task_definition      = "${aws_ecs_task_definition.aws-ecs-task.family}:${max(aws_ecs_task_definition.aws-ecs-task.revision, data.aws_ecs_task_definition.main.revision)}"
  launch_type          = "FARGATE"
  scheduling_strategy  = "REPLICA"
  desired_count        = var.app-replica-count-desired
  force_new_deployment = true

  network_configuration {
    subnets          = [var.private_subnet_ids_list[0]] # TODO: Run in multiple subnets?
    assign_public_ip = false
    security_groups = [
      aws_security_group.service_security_group.id,
      aws_security_group.load_balancer_security_group.id
    ]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn
    container_name   = "${var.resource-name-prefix}-container"
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.listener]
}

resource "aws_security_group" "service_security_group" {
  vpc_id      = var.vpc_id
  description = "ECS Security Group"
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.load_balancer_security_group.id]
    description     = "Allow traffic from load balancer"
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
