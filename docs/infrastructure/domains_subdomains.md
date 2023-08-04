When creating a rAPId instance you will need a hostname to be able to access the app in a secure way, there are few ways
to achieve this:

1. Using an existing domain from route53: AWS creates a hosted zone linked to your domain, just use this HZ id in the
inputs along the domain, and you are ready to go. (If the domain is currently being used, a subdomain can be created
automatically by providing the HZ id and the subdomain name in the `input-params.tfvars`).

2. Creating a new domain in route53: you will need to manually register a domain in the AWS console, once this is done
the steps are the same as scenario 1.

3. Using an existing domain outside AWS: you will need to leave the HZ id field empty and provide a
domain/subdomain, copy the NS values from the output and use them in your DNS provider.

4. Using an existing domain from a different AWS account to create a subdomain: you will need to leave the HZ id field
empty and provide the subdomain name, then copy the NS values from the output, go to the AWS
account that owns the domain, go to route 53, in the domain hosted zone, create a new record of the type NS with the
subdomain name and add the NS values copied from the outputs.
