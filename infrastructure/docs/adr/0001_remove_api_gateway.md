# 0001 - Remove Api Gateway
Date: 2022-02-22

## Status
Accepted

## Decision
We have removed the [AWS API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/limits.html) functionality (commit `d0e5361`) since the maximum payload for the gateway is 10Mb. We decided to use FastAPI to redirect to cognito for AUTH in the code itself.

## Future considerations
We have explored different options that could be considered in the future:
- Keep 10Mb limit
- Use [Kong](https://konghq.com/partners/aws/) (Recommended): It is OpenSource, it integrates with AWS and is scalable. Has not been implemented since it would take a lot of time and the use case does not justify its use right now.
- Use OTHER API gateway: They seem to need a license to operate and there were not many at the time.
- [LB](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html) handle redirect to Cognito: The ALB have a way to redirect traffic with the listeners.
- Write custom API gateway in EC2/ECS: Might be an option if only required for proxying.
- Write custom API gateway in [Lambda](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) (Not recommended): The maximum limit is 6Mb, even worse than the API Gateway itself.
