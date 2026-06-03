# Usage

The rAPId Frontend is a NextJS static site that serves as a user friendly wrapper to the API.

The Frontend provides easy access to the core actions within rAPId such as the ability to create schemas, upload and download data, as well as handling common user and client management.

Navigation is handled by a sidebar with the following sections, shown based on your permissions:

- **Catalog** — browse, search and open datasets you can read.
- **Add Dataset** — create a new schema from a sample file.
- **Jobs** — view the status of upload and query jobs.
- **User Admin** — create and modify users and clients.

> ## Demo Frontend coming soon!
>
> In lieu of a demo Frontend for you to use, here are some screenshots that demonstrate the functionality available.

## Managing Users

From the **User Admin** section you can browse all users and clients in a searchable, filterable table. Select a subject to modify its permissions, or use **Create subject** to add a new user or client and set their permissions.

![Create User](../diagrams/ui_create_user.png)

## Creating Schemas

From the **Add Dataset** section you can create a schema by specifying just the `sensitivity`, `layer`, `domain` and `dataset title` then uploading an example file of the data. rAPId will then infer the column names and types from the data and present them to you for review. You can then tweak them before submitting the schema for creation.

![Create Schema](../diagrams/ui_create_schema.png)

## Downloading Data

If a user has `READ` access to a dataset, they can open it from the **Catalog** and use the **Download** action on the dataset page to query and download its contents.

![Download Data](../diagrams/ui_download_data.png)

# Permissions

The Frontend automatically infers the permissions that the logged in user has access to and filters out what actions they can perform.

For example if a user does not have any user admin privileges then they will not be able to see any of the user and client creation interfaces.
