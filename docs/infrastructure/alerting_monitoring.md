The rAPId service comes with pre-configured alerts that are triggered when a log with level `ERROR` is produced by the application. In order to notify engineers of this type of alert, the parameter `support_emails_for_cloudwatch_alerts` must be defined with a list of emails that should receive alert notifications.

```
module "app_cluster" {
  source = "git::https://github.com/no10ds/rapid-infrastructure//modules//app-cluster"

  ...

  support_emails_for_cloudwatch_alerts = ["someone@email.com", "support@email.com"]

  ...
}
```

> Make sure to **confirm** the notification subscription in the email received from AWS in order to start receiving alerts.
