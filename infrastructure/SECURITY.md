# Security Notice

## What?

This is the security notice for all [No10 Data Science repositories](https://github.com/No10ds). The notice explains how vulnerabilities should be reported. Within Cabinet Office there are cyber security and information assurance teams, as well as security-conscious people within the programmes, that assess and triage all reported vulnerabilities.

## Reporting a Vulnerability

Cabinet Office and No10 are advocates of responsible vulnerability disclosure. If you’ve found a vulnerability, we would like to know so we can fix it. This notice provides details for how you can let us know about vulnerabilities, additionally you can view our [security.txt](https://vdp.cabinetoffice.gov.uk/.well-known/security.txt) file, here: <https://vdp.cabinetoffice.gov.uk/.well-known/security.txt>

You can report a vulnerability through our vulnerability disclosure programme at [HackerOne](https://hackerone.com/44c348eb-e030-4273-b445-d4a2f6f83ba8/embedded_submissions/new). Alternatively, you can send an email to [disclosure@digital.cabinet-office.gov.uk](mailto:disclosure@digital.cabinet-office.gov.uk); if you do this you may get a response from Zendesk, which is our ticketing system.

When reporting a vulnerability to us, please include:

- the website, page or repository where the vulnerability can be observed
- a brief description of the vulnerability
- details of the steps we need to take to reproduce the vulnerability
- non-destructive exploitation details

If you are able to, please also include:

- the type of vulnerability, for example, the [OWASP category](https://owasp.org/www-community/vulnerabilities/)
- screenshots or logs showing the exploitation of the vulnerability

[Reach out via email](mailto:disclosure@digital.cabinet-office.gov.uk) if you are not sure if the vulnerability is genuine and exploitable, or you have found:

- a non-exploitable vulnerability
- something you think could be improved - for example, missing security headers
- TLS configuration weaknesses - for example weak cipher suite support or the presence of TLS1.0 support

## Guidelines for reporting a vulnerability

When you are investigating and reporting the vulnerability on a gov.uk domain or subdomain, you must not:

- break the law
- access unnecessary or excessive amounts of data
- modify data
- use high-intensity invasive or destructive scanning tools to find vulnerabilities
- try a denial of service - for example overwhelming a service with a high volume of requests
- disrupt our services or systems
- tell other people about the vulnerability you have found until we have disclosed it
- social engineer, phish or physically attack our staff or infrastructure
- demand money to disclose a vulnerability

Only submit reports about exploitable vulnerabilities through HackerOne.

## Bug bounty

Unfortunately, Cabinet Office and No10 do not offer a paid bug bounty programme. We will make efforts to show appreciation to people who take the time and effort to disclose vulnerabilities responsibly. We do have [an acknowledgements page for legitimate issues found by researchers](https://vdp.cabinetoffice.gov.uk/thanks.txt).

---

#### Further reading and inspiration about responsible disclosure and `SECURITY.md`

- <https://www.gov.uk/help/report-vulnerability>
- <https://www.ncsc.gov.uk/information/vulnerability-reporting>
- <https://mojdigital.blog.gov.uk/vulnerability-disclosure-policy/>
- <https://github.com/Trewaters/security-README>
- <https://github.com/alphagov/security.txt>

