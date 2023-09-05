## List

Use this endpoint to list all available permissions that can be granted to users and clients.

### Permissions

`USER_ADMIN`

### Path

`GET /permissions`

### Outputs

List of permissions:

```json
["DATA_ADMIN", "USER_ADMIN", "WRITE_ALL", "READ_PROTECTED_<domain>", "..."]
```

## List Subject Permissions

Use this endpoint to list all permissions that are assigned to a subject.

### Permissions

`USER_ADMIN`

### Path

`GET /permissions/{subject_id}`

### Outputs

List of permissions:

```json
["DATA_ADMIN", "USER_ADMIN", "WRITE_ALL", "READ_PROTECTED_<domain>", "..."]
```
