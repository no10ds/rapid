terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 4.53.0"
      configuration_aliases = [aws.us_east]
    }
  }
}
