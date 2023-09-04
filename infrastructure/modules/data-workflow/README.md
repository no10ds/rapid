<!-- BEGIN_TF_DOCS -->

## Requirements

No requirements.

## Providers

| Name                                             | Version |
| ------------------------------------------------ | ------- |
| <a name="provider_aws"></a> [aws](#provider_aws) | 4.50.0  |

## Modules

No modules.

## Resources

| Name                                                                                                                                                                             | Type        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| [aws_athena_workgroup.rapid_athena_workgroup](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/athena_workgroup)                                      | resource    |
| [aws_cloudwatch_log_group.aws_glue_connection_error_log_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group)                 | resource    |
| [aws_cloudwatch_log_group.aws_glue_connection_log_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group)                       | resource    |
| [aws_cloudwatch_log_group.aws_glue_crawlers_log_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group)                         | resource    |
| [aws_glue_catalog_database.catalogue_db](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_catalog_database)                                      | resource    |
| [aws_glue_catalog_table.metadata](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_catalog_table)                                                | resource    |
| [aws_glue_connection.glue_connection](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_connection)                                               | resource    |
| [aws_iam_policy.crawler_s3_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy)                                                       | resource    |
| [aws_iam_role.glue_service_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role)                                                           | resource    |
| [aws_iam_role_policy_attachment.glue_service_role_managed_policy_attach](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource    |
| [aws_iam_role_policy_attachment.glue_service_role_s3_policy_attach](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment)      | resource    |
| [aws_s3_bucket.rapid_athena_query_results_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)                                         | resource    |
| [aws_s3_bucket_policy.athena_query_bucket_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy)                                  | resource    |
| [aws_s3_bucket_public_access_block.rapid_athena_query_results_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block) | resource    |
| [aws_security_group.glue_connection_sg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group)                                              | resource    |
| [aws_vpc_endpoint.s3_vpc_endpoint](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint)                                                     | resource    |
| [aws_availability_zones.available](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones)                                            | data source |
| [aws_prefix_list.s3_prefix](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/prefix_list)                                                          | data source |

## Inputs

| Name                                                                                          | Description                                                                             | Type          | Default                                           | Required |
| --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------- | :------: |
| <a name="input_aws_account"></a> [aws_account](#input_aws_account)                            | AWS Account number to host the rAPId service                                            | `string`      | n/a                                               |   yes    |
| <a name="input_aws_region"></a> [aws_region](#input_aws_region)                               | The region of the AWS Account for the rAPId service                                     | `string`      | n/a                                               |   yes    |
| <a name="input_data_s3_bucket_arn"></a> [data_s3_bucket_arn](#input_data_s3_bucket_arn)       | S3 Bucket arn to store application data                                                 | `string`      | n/a                                               |   yes    |
| <a name="input_data_s3_bucket_name"></a> [data_s3_bucket_name](#input_data_s3_bucket_name)    | S3 Bucket name to store application data                                                | `string`      | n/a                                               |   yes    |
| <a name="input_private_subnet"></a> [private_subnet](#input_private_subnet)                   | Application Private subnet                                                              | `string`      | n/a                                               |   yes    |
| <a name="input_resource-name-prefix"></a> [resource-name-prefix](#input_resource-name-prefix) | The prefix to add to resources for easier identification                                | `string`      | n/a                                               |   yes    |
| <a name="input_tags"></a> [tags](#input_tags)                                                 | A common map of tags for all VPC resources that are created (for e.g. billing purposes) | `map(string)` | <pre>{<br> "Resource": "data-f1-rapid"<br>}</pre> |    no    |
| <a name="input_vpc_id"></a> [vpc_id](#input_vpc_id)                                           | Application VPC                                                                         | `string`      | n/a                                               |   yes    |

## Outputs

| Name                                                                                                                                               | Description                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| <a name="output_athena_query_result_output_bucket_arn"></a> [athena_query_result_output_bucket_arn](#output_athena_query_result_output_bucket_arn) | Output S3 bucket ARN for Athena query results |
| <a name="output_athena_workgroup_arn"></a> [athena_workgroup_arn](#output_athena_workgroup_arn)                                                    | Query workgroup for Athena                    |
| <a name="output_glue_catalog_arn"></a> [glue_catalog_arn](#output_glue_catalog_arn)                                                                | Catalog database arn                          |
| <a name="output_tags"></a> [tags](#output_tags)                                                                                                    | The tags used in the project                  |

<!-- END_TF_DOCS -->
