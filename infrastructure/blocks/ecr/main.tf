terraform {
  backend "s3" {
    key = "ecr/terraform.tfstate"
  }
}

resource "aws_ecr_repository" "private" {
  #checkov:skip=CKV_AWS_51:No need for immutable tags
  name                 = "data-f1-registry"
  image_tag_mutability = "MUTABLE"
  tags                 = var.tags

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
  }
}

resource "aws_ecr_lifecycle_policy" "image_expiry_policies" {
  repository = aws_ecr_repository.private.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Retain PROD image",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["PROD"],
                "countType": "imageCountMoreThan",
                "countNumber": 9999
            },
            "action": {
                "type": "expire"
            }
        },
        {
            "rulePriority": 2,
            "description": "Expire old images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 5
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}


resource "aws_ecr_repository" "private_ckan" {
  #checkov:skip=CKV_AWS_51:No need for immutable tags
  name                 = "rapid-ckan"
  image_tag_mutability = "MUTABLE"
  tags                 = var.tags

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
  }
}

resource "aws_ecr_lifecycle_policy" "image_expiry_policies_ckan" {
  repository = aws_ecr_repository.private_ckan.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Retain PROD image",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["PROD"],
                "countType": "imageCountMoreThan",
                "countNumber": 9999
            },
            "action": {
                "type": "expire"
            }
        },
        {
            "rulePriority": 2,
            "description": "Expire old images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 5
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

resource "aws_ecrpublic_repository" "public" {
  provider = aws.us_east_1

  repository_name = "api"

  catalog_data {
    about_text = "Please see https://github.com/no10ds/rapid-infrastructure/ for more information"
    architectures = [
    "x86-64"]
    description = "Project rAPId API Image"
    # TODO: Add image
    # logo_image_blob   = filebase64(image.png)
    operating_systems = [
    "Linux"]
    usage_text = "Please see https://github.com/no10ds/rapid-infrastructure/ for details on the use"
  }
}

resource "aws_ecrpublic_repository" "public_ckan" {
  provider = aws.us_east_1

  repository_name = "ckan"

  catalog_data {
    about_text = "Please see https://github.com/no10ds/rapid-catalogue-module for more information"
    architectures = [
    "x86-64"]
    description = "Project rAPId CKAN Image"
    operating_systems = [
    "Linux"]
    usage_text = "Please see https://github.com/no10ds/rapid-catalogue-module for details on the use"
  }
}
