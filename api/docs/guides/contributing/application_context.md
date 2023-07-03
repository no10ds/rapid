# Application Context

## Assuming roles in AWS

This point is only applicable if the infra has been set up with our `iam-config` infra block.

To gain the admin privileges necessary for AWS, one needs to assume admin role. This will be enabled only for users
defined in the infra config after logging in the AWS console for the first time as an IAM user and enabling the MFA.

Assuming roles for the first time:

1) Log in
2) Enable MFA
3) Log out
4) Log in and introduce MFA code
5) Go to the user menu in the top right corner of the AWS console
6) Click on `Switch role`
7) Input the AWS account number
8) Input the role name (`resource-admin`/`resource-user`)
9) Click on `Switch Role`

### Considerations

- The admin role expires after 1 hour
- The user role expires after 2 hours
- Once a role has expired, all the access is revoked. To get access again you will need to log out and log in
- The user role has less access than the admin one, to check on specifics go to the AWS IAM role definitions or use
  the [AWS Policy Simulator](https://policysim.aws.amazon.com/home/index.jsp?#)

## Adding/Deleting permissions

###  New permissions

In Terraform, we define permissions for client apps and users.

In `modules/auth/variables.tf` we define two lists of permissions (Data and Admin). When running Terraform these are
created in DynamoDB and can be assigned to _client apps_.

In order to create a new category of permissions, you need to:

- Add/delete permissions from the list in Terraform
- Update the code in `api/application/services/authorisation_service.py` that matches client app permissions to handle
  the new scope(s)
- When adding a permission with a new sensitivity level (e.g., READ_SENSITIVE) or a new action (e.g., READ_USER), add it
  to `api/common/config/auth.py`
- Check if you need handle the permission in `api/application/services/authorisation/acceptable_permissions.py`

## Adding more statements into the firewall rules

We have enabled WAF rule to protect the application. It contains two statements: one allows access to the load balancer
only from our domain name and the second protects from SQL injection. You can add more statements into the WAF rule at
no extra cost. WAF rules are defined in `modules/app-cluster/load balancer.tf`
