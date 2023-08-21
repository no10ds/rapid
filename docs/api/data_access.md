There are various access levels that restrict permissions to datasets.

## Sensitivity

This is the mechanism by which we assign an access level to a dataset. It must be specified when the schema is created.

### Hierarchical Access

#### Values:

- `PRIVATE`
- `PUBLIC`

These sensitivity levels function as part of a hierarchy. Anyone with access to `PRIVATE` can also access `PUBLIC` but
not the reverse.

### Isolated Access

#### Values:

- `PROTECTED`

Protected datasets as isolated from the hierarchy and are domain specific. This means that you have to be granted access
to specific protected domains to gain access.

These domains must first be [created](/api/routes/protected_domain/#create) and then assigned to
a [client](/api/routes/client/#create) or [user](/api/routes/user/#create) for usage.
