# Application Limitations

This document outlines some limitations that currently restrict parts of the application and its usage.

## Large Dataset Upload Limitations

### Limitations

To handle large datasets, most of the processing is done asynchronously. This is because of several limitations:

1. The application resources are limited, and we cannot load a large (>500mb) file into volatile memory and process it
2. Browsers have a timeout when waiting for a response to be returned (typically 1-5 minutes)

### User experience

There are two main constraining factors to the user experience when uploading a dataset.

1. The user’s internet speed (particularly upload speed, see table below)
    1. We have seen 5GB files take >30mins on a slow connection and < 10mins on a fast one)
2. The time it takes to process the uploaded file in the background before it is able to be queried etc.

#### File upload and processing rough benchmarks

- `Time to process` refers to the time it takes to process the file once it has been saved to disk and until it is ready
  to be queried.

| File size | Upload speed | Time to upload | Time to process |
|-----------|--------------|----------------|-----------------|
| 20MB      | 3.7Mb/s      | 20s            | ~10s            |
| 200MB     | 3.7Mb/s      | 2mins          | ~1min 40s       |
| 780MB     | 3.7Mb/s      | 8mins          | ~7mins          |
| 780MB     | 17Mb/s       | 2mins          | ~7mins          |
| 5GB       | 17Mb/s       | 10mins         | ~35mins         |

### Possible improvements

Potential areas to focus on to improve performance could be:

1. Increase the application resource allowances (CPU and Memory) to improve processing time
    1. Increase the chunk size in which the uploading file is stored to disk. Currently we use a 50MB chunk size but
       this could be over 100-200MB.
    2. Allow larger chunks of data to be processed (currently we process 200,000 rows at a time, but this could be well
       over 1,000,000 if sufficient memory were available)
2. Provide a pre-signed URL to upload the file directly to S3 and then use AWS tools (Lambda, Glue, etc.) to perform
   processing exclusively in ‘the cloud’.
3. The maximum file size that can be uploaded is now restricted by the persistent storage available to the application.
   This is currently 20GB,
   however [could be increased up to 200GB](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-storage.html)
   .

## Performance limitations

There are few areas that are bottlenecks:

- Double upload
    - During the upload flow two uploads are performed:
        1. The entire raw file to S3
        2. The entire partitioned dataset to S3
    - This could be optimised
- No caching
    - Could look at caching query results (beyond what comes out of the box with Athena)
    - Caching responses for other endpoints if no changes have occurred in the meantime

## Security

### Logging & Request Tracing

We currently do not have widespread logging coverage.

Logging is not occurring for at least:

- Logins
- Permission denied operations
- Who performed which operations

Additionally, support for passing a request ID through the different levels of the application stack exists, but has not
been fully completed.

### SQL Injection

- We are currently not checking for SQL injection in the code beyond what the firewall (WAF) rules give us.
    - The WAF has an allocated time budget to check the request so if the request is large or the processing is slow for
      whatever reason there is a risk that malicious code could be introduced.

### Caching requests - Cache-Control header

By default, caching is enabled. If this functionality wants to be removed for security purposes:
- Add the 'Cache-Control' header to the response object in the controller. Example:
```
return templates.TemplateResponse(
        name="name.html",
        context={"request": request},
        headers={"Cache-Control": "no-store"},
    )
```
- Add `common.js` into the script section of the template. Example:
```
<script type="text/javascript">
    {% include "./js/common.js" %}
</script>
```
- Add a call to the method `handleBrowserNavigation();` on the page's `<file-name>.js` file.

### Security headers

As part of our security efforts we have added some
[OWASP recommended security headers](https://owasp.org/www-project-secure-headers/). However, there are still some
improvements that are needed:
1. Remove/Change the use of `unsafe-inline` from the `script-src` section of the CSP Headers, read
[here](https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/nonce) for a possible solution.
2. The report CSP Header can be deleted to not show logs in the console or updated to show areas of improvements.
3. More headers can be added, the ones provided right now are a sensible default.

If there is no previous knowledge on how to create/add info on the CSP Headers, find some information
[here](https://www.uriports.com/blog/creating-a-content-security-policy-csp/)

- To Enable XSS protection in
  WAF [OWASP XSS Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- To Enable CSP headers and restrict inline styling and inline
  scripting [OWASP CSP Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- To Use the CSRF header for security checks (the CSRF header is enabled by
  default) [OWASP CSRF Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

### Tracing requests
Whenever a call is made to an endpoint, the subject id of the caller will be logged in cloudwatch, we recommend
creating a request id and log it during the processing, to get an e2e picture of what is happening and track the
changes made by a particular subject.
