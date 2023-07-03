# Clean up dynamically created resources 🧹

Through repeated manual testing, both by the rAPId team and the client, we have found that it would be helpful to have a dataset `delete` endpoint. Additionally, this would be useful and convenient for the eventual departmental users.

Since we do not have the time to do this, it was decided to create a checklist for deleting a dataset.

## Resources to delete ❌

AWS console access is needed in order to delete these resources, the user needs to have enough permissions to do so.

Until the ```delete``` endpoint is created for cleanup, we recommend following these steps even if there are other ways to delete certain data (for example using the ```delete``` endpoint for the raw files).

### Schema 🔠

#### Steps 🚶‍

- Access the AWS console and log in
- Go to S3
- Go to the bucket `{prefix}-data-ingest-raw-data`
- Go to `/data/schemas/{sensitivity}/{domain}/{dataset}/{version}`
- Select the file `schema.json`
- Click on delete
- Follow the instructions provided by the console

#### Consequence if not deleted 😿

- Nobody would be able to upload a new schema with the same domain and dataset while it is in place
- If the crawler/tables has been deleted the users will be able to upload the data but not to query it

### Data 📈

#### Steps 🚶‍

- Access the AWS console and log in
- Go to S3
- Go to the bucket `{prefix}-data-ingest-raw-data`
- Go to `/data/{domain}/`
- Select the `dataset` folder or the `{version}` subdirectory within the dataset
- Click on delete
- Follow the instructions provided by the console

#### Consequence if not deleted 😿

- All the data will be retained and the user would be able to query if the crawlers are retained
- If a new schema is uploaded with the same domain/dataset, then the crawler will add the old files to the new table

### Raw data 🧾

#### Steps 🚶‍

- Access the AWS console and log in
- Go to S3
- Go to the bucket `{prefix}-data-ingest-raw-data`
- Go to `/raw_data/{domain}/`
- Select the `dataset` folder
- Click on delete
- Follow the instructions provided by the console

#### Consequence if not deleted 😿

- The data will be retained but never used, we recommend enabling some sort of retention policy to delete the raw files after some time to avoid this issue

### Crawler 🕷️

⚠️ Only delete the crawler if all versions of a dataset are also deleted. We use one crawler for all versions of the dataset.

#### Steps 🚶‍

- Access the AWS console and log in
- Go to AWS Glue
- Go to crawlers
- Select the crawler `{prefix}_crawler/{domain}/{dataset}`
- Click on Action
- Click on Delete crawler
- Follow the instructions provided by the console

#### Consequence if not deleted 😿

- It will be maintained and can be run but will throw errors if the files are deleted
- Nobody would be able to upload a new schema with the same domain and dataset while it is in place
- If someone makes a request to the `list` dataset endpoint, this dataset will be on the list

### Glue catalog table 🗄

#### Steps 🚶‍

- Access the AWS console and log in
- Go to AWS Glue
- Go to Tables
- Select the table `{domain}_{dataset}_{version}`
- Click on Action
- Click on Delete table
- Follow the instructions provided by the console

#### Consequence if not deleted 😿

- The data will be accessible by Athena and the `query` endpoint

### Protected domains 🥽

#### Steps 🚶‍

- Access the script within the api `test/scripts/delete_protected_domain_permission`
- Specify the domain you would like to delete

```commandline
python test/scripts/delete_protected_domain_permission domain-to-be-deleted
```

#### Items deleted

- Protected domain permission from database `READ` and `WRITE`
- Removes permission assigned to users
- Removes protected datasets within domain, this includes:
  - Crawler
  - Table
  - Data (raw data and data)
  - Schema

## Notes 📝

- `{prefix}` is a value assigned in terraform as part of the IaC, in our case is `rapid` and it is maintained across resources
