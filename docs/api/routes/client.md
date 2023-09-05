## Create

As a maintainer of a rAPId you can create new clients to interact with the API to upload or query data.

### Permissions

`USER_ADMIN`

### Path

`POST /client`

### Inputs

| Parameters       | Usage             | Example values | Definition                                                                |
| ---------------- | ----------------- | -------------- | ------------------------------------------------------------------------- |
| `client details` | JSON Request Body | See below      | The name of the client application to onboard and the granted permissions |

```json
{
  "client_name": "department_for_education",
  "permissions": ["READ_ALL", "WRITE_PUBLIC"]
}
```

#### Client Name

The client name must adhere to the following conditions:

- Alphanumeric
- Start with an alphabetic character
- Can contain any symbol of `. - _ @`
- Must be between 3 and 128 characters

### Outputs

Once the new client has been created, the following information is returned in the response:

```json
{
  "client_name": "department_for_education",
  "permissions": ["READ_ALL", "WRITE_PUBLIC"],
  "client_id": "1234567890-abcdefghijk",
  "client_secret": "987654321"
}
```

## Delete

Given a client already exists you can delete them from rAPId using the relevant client ID.

### Permissions

`USER_ADMIN`

### Path

`DELETE /client/{client_id}/`

### Outputs

Confirmation Message:

```json
{
  "message": "The client '{client_id}' has been deleted"
}
```
