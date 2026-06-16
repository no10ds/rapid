terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 2.7.0"
      configuration_aliases = [aws.default, aws.us_east]
    }
    github = {
      source = "integrations/github"
    }
  }
}
