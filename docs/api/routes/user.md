## Create

As a maintainer of a rAPId you can create new users to interact with the API to upload or query data, generate their credentials and add permissions to them.

### Permissions

`USER_ADMIN`

### Path

`POST /user`

### Inputs

| Parameters     | Usage             | Example values | Definition                                                              |
| -------------- | ----------------- | -------------- | ----------------------------------------------------------------------- |
| `User details` | JSON Request Body | See below      | The name of the user application to onboard and the granted permissions |

```json
{
  "username": "john_doe",
  "email": "john.doe@email.com",
  "permissions": ["READ_ALL", "WRITE_PUBLIC"]
}
```

#### Username

The username must adhere to the following conditions:

- Alphanumeric
- Start with an alphabetic character
- Can contain any symbol of `. - _ @`
- Must be between 3 and 128 characters

#### Email address

The email must adhere to the following conditions:

- The domain must be included on the `ALLOWED_EMAIL_DOMAINS` environment
- Must satisfy the Email Standard Structure `RFC5322` (
  see [Email Address in Wikipedia](https://en.wikipedia.org/wiki/Email_address))

### Outputs

Once the new user has been created, the following information will be shown in the response:

```json
{
  "username": "jhon_doe",
  "email": "jhon.doe@email.com",
  "permissions": ["READ_ALL", "WRITE_PUBLIC"],
  "user_id": "some-generated-id-eq2e3q-eqwe32-12eqwe214q"
}
```

## Delete

Given a user already exists you can delete them from rAPId.

### Permissions

`USER_ADMIN`

### Path

`DELETE /user`

### Inputs

| Parameters     | Usage             | Example values | Definition                            |
| -------------- | ----------------- | -------------- | ------------------------------------- |
| `user details` | JSON Request Body | See below      | The name and id of the user to delete |

```json
{
  "username": "John Doe",
  "user_id": "some-uuid-generated-string-asdasd0-2133"
}
```

### Outputs

Confirmation Message:

```json
{
  "message": "The user '{username}' has been deleted"
}
```
