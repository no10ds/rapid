# Getting Started

This guide will walk you through getting started with rAPId.

This walkthrough is for the `/docs` endpoint, everything done here can also be done programmatically.

## Authorising

To authorise with this rAPId instance, you need to click the `authorize` button at the top right of the page.

Then enter the values for `client_id` and `client_secret` that you should have been given.

Contact your administrator of rAPId if you do not have these.

## Uploading your first dataset

### Getting a dataset

We will need a dataset to upload, this must be in the format of a csv. If you have one already then you can skip this.

If you do not then you can use the one at the link below.

https://raw.githubusercontent.com/Geoyi/Cleaning-Titanic-Data/master/titanic_clean.csv

This needs to be saved locally on your computer. To do this you can do one of the two options below:

1. Run the command:
    ```
    curl https://raw.githubusercontent.com/Geoyi/Cleaning-Titanic-Data/master/titanic_clean.csv -o titanic.csv
    ```

2. Copy the contents of the data in the link into a blank file and save it as a CSV called `titanic.csv`


### Creating a schema

Before we can upload a dataset, we need to create a schema for it so that rAPId knows what the dataset is expected to look like.

> Note: You only have to do this the first time you upload a particular dataset.

To do this, scroll down to the `Schema` section on the webpage and click on the `Generate Schema` endpoint to expand its contents.

To use it, you need to click `Try it out` on the right of the page and then enter the necessary information about your dataset. Let's use the values:

- `sensitivity`: `PUBLIC`
- `domain`: `demo`
- `dataset`: `titanic`

Below, in the `Request body`, you can click `Browse` to select your dataset and then `Execute` at the bottom to hit the API with this information.

The API will then infer the schema from the dataset and produce a JSON schema that among other things will contain the column names and types.

This JSON can be found below in the `Response body` and can be copied with a button in the bottom right of the response.

We can take this JSON and navigate to the next API endpoint, `Upload Schema`. Expand this, click `Try it out` and paste the JSON schema into the `Request body`, replacing what was previously there.

We now need to edit a couple of values that weren't generated for us. These are `name` and `email`, every dataset needs to have an owner. Other values can be changed at this point too if you wish to alter the default behaviour. [Here](schema_creation.md) is the schema creation documentation for more info.

Once you are happy with the schema, click `Execute` and it will be created!

### Uploading a dataset

Now that the schema exists, we can upload our dataset.

Navigate to the `Upload Data` endpoint under `Datasets`. Expand this, click `Try it out`, enter `demo` for `domain` and `titanic` for `dataset`, click `Browse` to select the file and finally click `Execute` to upload the dataset.

The dataset will now be processed and within a few minutes will be available to query.

### Query a dataset

To query your dataset, navigate to the `Query Dataset` endpoint and enter the same information that you did above.

When you click execute you should see your data in the response!

If your dataset is large you may want to pass the below into the `Request body` to limit the number of rows that are returned at once.

    ```
    {"limit": "100"}
    ```

[Here](usage.md#query-dataset) is more documentation on forming the query body.
