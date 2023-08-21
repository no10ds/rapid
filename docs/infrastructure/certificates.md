When creating a rAPId instance a certificate will be needed in order to serve the application in HTTPS, there are 2 scenarios:

1. The AWS account already has a certificate for the domain you are using (this might be true for the first and second scenario when [managing domains/subdomains](#managing-domainssubdomains)), in which case you can provide the certificate arn for it to be used in the load balancer in the `input-params.tfvars`).

2. The AWS account does not have a certificate for the domain you plan to use, (this might be true for the third and fourth scenario when [managing domains/subdomains](#managing-domainssubdomains)), in which case you need to leave the certificate information empty in the `input-params.tfvars`).

[AWS can not use the certificate from a different account](https://aws.amazon.com/premiumsupport/knowledge-center/acm-export-certificate/#:~:text=You%20can't%20export%20an,AWS%20Region%20and%20AWS%20account.), and therefore you will be required to create a new one (this will be handled automatically).
