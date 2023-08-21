## Create

Protected domains can be created to restrict access permissions to specific domains. Use this endpoint to create a new protected domain. After this you can create clients with the permission for this domain and create `PROTECTED` datasets within this domain.

### Permissions

`DATA_ADMIN`

### Path

`POST /protected_domains/{domain}`

### Inputs

| Parameters       | Usage               | Example values   | Definition                       |
|------------------|---------------------|------------------|----------------------------------|
| `domain`         | URL Parameter       | `land`           | The name of the protected domain |

## List

Use this endpoint to list the protected domains that currently exist.

### Permissions

`DATA_ADMIN`

### Path

`GET /protected_domains`

### Outputs

List of protected permissions in json format in the response body:

```json
[
  "land",
  "department"
]
```
