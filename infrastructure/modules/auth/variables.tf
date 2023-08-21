variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
  default = {
    Resource = "data-f1-rapid"
  }
}

variable "domain_name" {
  type        = string
  description = "Domain name for the rAPId instance"
}

variable "rapid_client_explicit_auth_flows" {
  type        = list(string)
  description = "The list of auth flows supported by the client app"
  default     = ["ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_CUSTOM_AUTH", "ALLOW_USER_SRP_AUTH"]
}

variable "rapid_user_login_client_explicit_auth_flows" {
  type        = list(string)
  description = "The list of auth flows supported by the user login app"
  default     = ["ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"]
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}

variable "password_policy" {
  type = object({
    minimum_length                   = number
    require_lowercase                = bool
    require_numbers                  = bool
    require_symbols                  = bool
    require_uppercase                = bool
    temporary_password_validity_days = number
  })
  description = "The Cognito pool password policy"
  default = {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }
}

variable "permissions_table_name" {
  type        = string
  description = "The name of the users permissions table in DynamoDb"
  default     = "users_permissions"
}

variable "scopes" {
  type = list(map(any))
  default = [
    {
      scope_name        = "CLIENT_APP"
      scope_description = "Client app default access"
    },
  ]
}

variable "admin_permissions" {
  type = map(map(any))
  default = {
    "USER_ADMIN" = {
      type = "USER_ADMIN"
    },
    "DATA_ADMIN" = {
      type = "DATA_ADMIN"
    },
  }
}

variable "master_data_permissions" {
  type = map(map(any))
  default = {
    "READ_ALL" = {
      type        = "READ"
      sensitivity = "ALL"
      layer       = "ALL"
    },
    "WRITE_ALL" = {
      type        = "WRITE"
      sensitivity = "ALL"
      layer       = "ALL"
    },
  }
}

variable "global_data_sensitivities" {
  type    = list(string)
  default = ["PUBLIC", "PRIVATE"]
}

variable "data_actions" {
  type    = list(string)
  default = ["READ", "WRITE"]
}

variable "layers" {
  type        = list(string)
  description = "A list of the layers that the rAPId instance will contain"
  default     = ["default"]
}
