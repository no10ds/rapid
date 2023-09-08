# Deployment

We provide two options for deploying rAPId within an AWS environment:

1. If you have existing infrastructure (e.g a VPC) that you would like to deploy rAPId within, then you can use the [rAPId module](/infrastructure/deployment/existing/), passing in specific variables relating to your AWS account.
2. If you do not have any existing infrastructure, you can instead deploy the [entire rAPId stack](/infrastructure/deployment/full_stack/) creating all the relevant infrastructure.

# Usage

Once the rAPId instance is spun up you can navigate to the API documentation at `https://<rAPId URL>/api/docs` to see the swagger docs for all the rAPId endpoints. The rAPId UI can be seen at `https://<rAPId URL>/`.

When the infrastructure is first created a default user is created and stored within your AWS Secrets Manager. This default user allows you access onto the rAPId instance and can be used to create other users and clients.

Navigate to your AWS account and under secrets manager find the `<rAPId-prefix>_UI_TEST_USER` secret. The secret will contain a `username` and `password` value that you can use to sign in to the rAPId UI. It is recommended that you create unique accounts for every user that will be using rAPId and not this default user created by the infrastructure.

# Developing

Alternatively you can run rAPId locally for development. For more details, please see the [contributing section](/contributing/).
