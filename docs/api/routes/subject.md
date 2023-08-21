## List

Use this endpoint to list subjects, both human users and client apps.

### Permissions

`USER_ADMIN`

### Path

`GET /subjects`

### Outputs

List of subjects:

```json
[
  {
    "subject_id": "<subject_id>",
    "subject_name": "<username>",
    "type": "USER"
  },
  {
    "subject_id": "<subject_id>",
    "subject_name": "<client_app_name>",
    "type": "CLIENT"
  }
]
```

## Modify Subject Permissions

Use this endpoint to modify the permissions that are granted to users and clients.

### Permissions

`USER_ADMIN`

### Path

`PUT /subjects/permissions`

### Inputs

| Parameters            | Usage               | Example values   | Definition                             |
|-----------------------|---------------------|------------------|----------------------------------------|
| `Subject Permissions` | JSON Request Body   | See below        | The details used to modify permissions |

```json
{
  "subject_id": "123456789",
  "permissions": [
    "READ_ALL",
    "WRITE_PUBLIC"
  ]
}
```

### Outputs

Confirmation of permissions:

```json
{
  "subject_id": "123456789",
  "permissions": [
    "READ_ALL",
    "WRITE_PUBLIC"
  ]
}
```
