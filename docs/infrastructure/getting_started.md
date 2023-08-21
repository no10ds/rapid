### Building blocks

After the backend has been created the building blocks are:

- [**app-cluster**](blocks/app-cluster):
    - LB resources setup
    - domain/routing setup
    - ecs setup
    - firewall rules setup
    - access setup/management for the app to aws resources
    - DynamoDB setup
- [**auth**](blocks/auth):
    - cognito user pool setup
    - resource server setup
    - client app setup
    - DynamoDB setup
- [**data-workflow**](blocks/data-workflow):
    - athena setup
    - crawlers setup
    - glue resources setup
- [**iam-config**](blocks/iam-config):
    - iam users setup
    - iam roles/resources setup
    - config and infrastructure checks (avoid common pitfalls)
- [**s3**](blocks/s3):
    - data storage setup
- [**vpc**](blocks/vpc):
    - vpc setup
    - public/private subnets setup
- [**ui**](blocks/ui):
    - public S3 bucket
    - download & upload static html files
    - create cloudfront cdn

More formally the infrastructure blocks have been organised bearing in mind the cadence of change. They are organised in
separate folders so that they each have their own remote Terraform state file:

```
├── blocks
│   ├── auth
│   ├── app-cluster
│   ├── data-workflow
│   ├── ecr
│   ├── iam-config
│   ├── pipeline
│   ├── s3
│   ├── vpc
│   └── ui
```
