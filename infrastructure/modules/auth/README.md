<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |
| <a name="provider_random"></a> [random](#provider\_random) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cognito_resource_server.rapid_resource_server](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_resource_server) | resource |
| [aws_cognito_user.ui_test_user](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user) | resource |
| [aws_cognito_user_pool.rapid_user_pool](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool) | resource |
| [aws_cognito_user_pool_client.e2e_test_client_data_admin](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_client) | resource |
| [aws_cognito_user_pool_client.e2e_test_client_read_and_write](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_client) | resource |
| [aws_cognito_user_pool_client.e2e_test_client_user_admin](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_client) | resource |
| [aws_cognito_user_pool_client.e2e_test_client_write_all](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_client) | resource |
| [aws_cognito_user_pool_client.test_client](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_client) | resource |
| [aws_cognito_user_pool_client.user_login](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_client) | resource |
| [aws_cognito_user_pool_domain.rapid_cognito_domain](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cognito_user_pool_domain) | resource |
| [aws_dynamodb_table.permissions_table](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_dynamodb_table_item.admin_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_dynamodb_table_item.data_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_dynamodb_table_item.test_client_data_admin_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_dynamodb_table_item.test_client_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_dynamodb_table_item.test_client_read_and_write_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_dynamodb_table_item.test_client_user_admin_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_dynamodb_table_item.test_client_write_all_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_dynamodb_table_item.ui_test_user_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table_item) | resource |
| [aws_secretsmanager_secret.client_secrets_cognito](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret.e2e_test_client_data_admin](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret.e2e_test_client_read_and_write](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret.e2e_test_client_user_admin](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret.e2e_test_client_write_all](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret.ui_test_user](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret.user_secrets_cognito](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret_version.client_secrets_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_secretsmanager_secret_version.e2e_test_client_data_admin_secrets_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_secretsmanager_secret_version.e2e_test_client_read_and_write_secrets_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_secretsmanager_secret_version.e2e_test_client_user_admin_secrets_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_secretsmanager_secret_version.e2e_test_client_write_all_secrets_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_secretsmanager_secret_version.ui_test_user_secrets_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_secretsmanager_secret_version.user_login_client_secrets_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [random_password.password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/password) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_region.region](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_admin_permissions"></a> [admin\_permissions](#input\_admin\_permissions) | n/a | `map(map(any))` | <pre>{<br>  "DATA_ADMIN": {<br>    "type": "DATA_ADMIN"<br>  },<br>  "USER_ADMIN": {<br>    "type": "USER_ADMIN"<br>  }<br>}</pre> | no |
| <a name="input_data_permissions"></a> [data\_permissions](#input\_data\_permissions) | n/a | `map(map(any))` | <pre>{<br>  "READ_ALL": {<br>    "sensitivity": "ALL",<br>    "type": "READ"<br>  },<br>  "READ_PRIVATE": {<br>    "sensitivity": "PRIVATE",<br>    "type": "READ"<br>  },<br>  "READ_PUBLIC": {<br>    "sensitivity": "PUBLIC",<br>    "type": "READ"<br>  },<br>  "READ_SENSITIVE": {<br>    "sensitivity": "SENSITIVE",<br>    "type": "READ"<br>  },<br>  "WRITE_ALL": {<br>    "sensitivity": "ALL",<br>    "type": "WRITE"<br>  },<br>  "WRITE_PRIVATE": {<br>    "sensitivity": "PRIVATE",<br>    "type": "WRITE"<br>  },<br>  "WRITE_PUBLIC": {<br>    "sensitivity": "PUBLIC",<br>    "type": "WRITE"<br>  },<br>  "WRITE_SENSITIVE": {<br>    "sensitivity": "SENSITIVE",<br>    "type": "WRITE"<br>  }<br>}</pre> | no |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | Domain name for the rAPId instance | `string` | n/a | yes |
| <a name="input_password_policy"></a> [password\_policy](#input\_password\_policy) | The Cognito pool password policy | <pre>object({<br>    minimum_length                   = number<br>    require_lowercase                = bool<br>    require_numbers                  = bool<br>    require_symbols                  = bool<br>    require_uppercase                = bool<br>    temporary_password_validity_days = number<br>  })</pre> | <pre>{<br>  "minimum_length": 8,<br>  "require_lowercase": true,<br>  "require_numbers": true,<br>  "require_symbols": true,<br>  "require_uppercase": true,<br>  "temporary_password_validity_days": 7<br>}</pre> | no |
| <a name="input_permissions_table_name"></a> [permissions\_table\_name](#input\_permissions\_table\_name) | The name of the users permissions table in DynamoDb | `string` | `"users_permissions"` | no |
| <a name="input_rapid_client_explicit_auth_flows"></a> [rapid\_client\_explicit\_auth\_flows](#input\_rapid\_client\_explicit\_auth\_flows) | The list of auth flows supported by the client app | `list(string)` | <pre>[<br>  "ALLOW_REFRESH_TOKEN_AUTH",<br>  "ALLOW_CUSTOM_AUTH",<br>  "ALLOW_USER_SRP_AUTH"<br>]</pre> | no |
| <a name="input_rapid_user_login_client_explicit_auth_flows"></a> [rapid\_user\_login\_client\_explicit\_auth\_flows](#input\_rapid\_user\_login\_client\_explicit\_auth\_flows) | The list of auth flows supported by the user login app | `list(string)` | <pre>[<br>  "ALLOW_REFRESH_TOKEN_AUTH",<br>  "ALLOW_USER_SRP_AUTH"<br>]</pre> | no |
| <a name="input_resource-name-prefix"></a> [resource-name-prefix](#input\_resource-name-prefix) | The prefix to add to resources for easier identification | `string` | n/a | yes |
| <a name="input_scopes"></a> [scopes](#input\_scopes) | n/a | `list(map(any))` | <pre>[<br>  {<br>    "scope_description": "Client app default access",<br>    "scope_name": "CLIENT_APP"<br>  }<br>]</pre> | no |
| <a name="input_tags"></a> [tags](#input\_tags) | A common map of tags for all VPC resources that are created (for e.g. billing purposes) | `map(string)` | <pre>{<br>  "Resource": "data-f1-rapid"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cognito_client_app_secret_manager_name"></a> [cognito\_client\_app\_secret\_manager\_name](#output\_cognito\_client\_app\_secret\_manager\_name) | Secret manager name where client app info is stored |
| <a name="output_cognito_user_app_secret_manager_name"></a> [cognito\_user\_app\_secret\_manager\_name](#output\_cognito\_user\_app\_secret\_manager\_name) | Secret manager name where user login app info is stored |
| <a name="output_cognito_user_pool_id"></a> [cognito\_user\_pool\_id](#output\_cognito\_user\_pool\_id) | The Cognito rapid user pool id |
| <a name="output_rapid_test_client_id"></a> [rapid\_test\_client\_id](#output\_rapid\_test\_client\_id) | The rapid test client id registered in the user pool |
| <a name="output_resource_server_scopes"></a> [resource\_server\_scopes](#output\_resource\_server\_scopes) | The scopes defined in the resource server |
| <a name="output_user_permission_table_arn"></a> [user\_permission\_table\_arn](#output\_user\_permission\_table\_arn) | The arn of the dynamoDB table that stores permissions |
| <a name="output_user_permission_table_name"></a> [user\_permission\_table\_name](#output\_user\_permission\_table\_name) | The name of the dynamoDB table that stores permissions |
| <a name="output_user_pool_endpoint"></a> [user\_pool\_endpoint](#output\_user\_pool\_endpoint) | The Cognito rapid user pool endpoint |
<!-- END_TF_DOCS -->
