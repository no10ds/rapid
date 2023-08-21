The core primitive of rAPId is the schema. A schema is a JSON file that defines the structure of a dataset. It is used to validate data uploaded to rAPId and to provide a consistent interface for querying data.

The first step is to define a schema that contains the desired data structure, a schema can either be created [from scratch](#from-scratch) or auto-generated from a [sample data file](#auto-generated).

## Structure

A schema is defined with the following structure:

### Metadata

#### General information of the schema.

  - `layer` - String value, this is the name of the layer within rAPId that you wish to place the dataset within. The possible values of this are unique to the rAPId instance and specified on creation. If none is provided, the option will be `default`.
  - `domain` - String value, is the name of the domain that owns the dataset, it could be for example the name of the department that handles the data.
  - `dataset` - String value, is the name of the dataset. e.g.: "receipts" or "address".
  - `sensitivity` - String value, is the sensitivity level of the dataset. e.g.: "PUBLIC", "PRIVATE", "PROTECTED"
  - `description` - Free text string that provides human readable information about the details of the dataset.
  - `version` - int value, denotes the schema version
  - `key_value_tags` - Dictionary of string keys and values to associate to the dataset. e.g.: `{"school_level": "primary", "school_type": "private"}`
  - `key_only_tags` - List of strings of tags to associate to the dataset. e.g.: `["schooling", "benefits", "archive", "historic"]`
  - `update_behaviour` - String value, the action to take when a new file is uploaded. e.g.: `APPEND`, `OVERWRITE`.

### Columns

#### A list defining the columns that are to be expected within the dataset.

  - `name` - String value, name of the column.
  - `data_type` - String value, this is an accepted pandas' data type, will be used to validate the schema.
  - `allow_null` - Boolean value, specifies whether the columns can have empty values or not.
  - `partition_index` (Optional) - Integer value, whether the column is a [partition](#partitions) and its index.
  - `format` (Conditional) - String value, regular expression used to specify the format of the dates. Will only be used and required if the data_type is date.

### Sensitivity
The sensitivity level of a dataset can be described by one of three values: `PUBLIC`, `PRIVATE` and `PROTECTED`.
These determine the access level that different clients will have to the data depending on their permissions.

Notes if you wish to use the sensitivity level `PROTECTED` then you must first create a Protected Domain for your Dataset. See the [data access docs](data_access.md)

### Description
The description is where you can specify human readable details about the dataset so that a user can quickly understand the contents and purpose of a dataset.

### Version
The schema version is automatically generated and cannot be updated by the user

### Tags
You can add up to 30 custom tags to a dataset. These are in a key: value format which allow for identification and categorisation of the datasets.

Restrictions applying to the keys:
- Only alphanumeric characters, hyphens and underscores
- Length between 1 and 128 characters

Restrictions applying to the values:
- Only alphanumeric characters, hyphens and underscores
- Length between 0 and 256 characters

### Owners
You must specify at least one dataset owner.

Typically this is a point of contact if there are issues or questions surrounding the dataset.

You MUST change the default values, otherwise an error will be thrown and schema upload will fail.

### Update Behaviour
The behaviour of the API when a new file is uploaded to the dataset. The possible values are:
- `APPEND` - New files will be added to the dataset, there are no duplication checks so new data must be unique. This is the default behaviour.
- `OVERWRITE` - Any new file will overwrite the current content. The overwrite will happen on the partitions, so if there is an old partition that is not included in the new dataset, that will not be overwritten.

### Column headings
Column heading names should follow a strict format. The [requirements](https://docs.aws.amazon.com/glue/latest/dg/add-classifier.html) are:
- Lowercase
- No whitespace
- No other punctuation except underscores, but not be exclusively underscores
- CAN include digits, but not be exclusively digits

### Accepted data types
The data accepted data types for a rAPId instance can be found detailed [here](https://docs.aws.amazon.com/athena/latest/ug/data-types.html). The only Athena types that are currently unsupported are array, map and struct types.

- `integer` - Use it to define integer values.
- `double` - Use it to define float values.
- `string` - Use it to define string.
- `date` - Use it to define date objects, then in the format key specify the desired [date-format](#date-formats).
- `boolean` - Use it to define boolean values (see Booleans section below).

### Date formats

The date columns are required to have a format in oder to parse in the dataframe, the year (%Y) and month (%m) will be required,
the day (%d) is optional and a separator ('/' or '-') must be in place. Accepted format examples for the 21st of January 2021:

- %Y/%m/%d -> 2021/01/21
- %d/%m/%Y -> 21/01/2021
- %m/%d/%Y -> 01/21/2021
- %Y-%m-%d -> 2021/01/21
- %d-%m-%Y -> 21-01-2021
- %m-%d-%Y -> 01-21-2021
- %Y/%m -> 2021/01
- %m/%Y -> 01/2021
- %Y-%m -> 2021-01
- %m-%Y -> 01-2021

### Booleans

In order to handle nullables we have introduced [pandas' boolean nullable data type](https://pandas.pydata.org/pandas-docs/stable/user_guide/boolean.html),
nullable boolean values can be 'NA', 'null' or an empty value. However, 'None' is not accepted.

When retrieving the data the null values will be returned as an empty object '{}'.

### Partitions 🗂

In order to make the application more efficient in terms of time and money when querying, we added an automatic [AWS glue partition](https://aws.amazon.com/blogs/big-data/work-with-partitioned-data-in-aws-glue/)
maker in the rAPId service, in order to use it, just add an integer into the partition_index when creating a schema.

The partition columns must:
- Start with 0 as the first index.
- Be a positive integer.
- Be sequential (0, 1, 2, ... N), the lower the index number the higher the hierarchy.
- Not allow null values.
- At least one column should not be a partition.

This means the partitions will always start from 0 and end with `partition_size - 1` as the last index. Let's imagine we have a dataset with 2 columns as partitions since `2 - 1 = 1`, then, the partition indexes must be 0 and 1. for a dataset with 3 partitions
`3 - 1 = 2`, therefore, the indexes must be 0, 1, and 2.

For the hierarchy, let's imagine we have 3 columns, "year" with index=0, month with index=1 and "region" with index=2. Then, the partition hierarchy will be similar to this:

```
year=year1
├── month=month1
│   ├── region=region1
│   └── region=region2
└──  month=month2
    ├── region=region1
    └── region=region2
year=year2
├── month=month1
│   ├── region=region1
│   └── region=region2
└── month=month2
    ├── region=region1
    └── region=region2
```

## From scratch

To create a schema manually from scratch, just create a json file filling all the required values from the Structure section following this example:

```json
{
  "metadata": {
    "domain": "my_domain_name",
    "dataset": "my_dataset_name",
    "description": "",
    "sensitivity": "SENSITIVITY",
    "key_value_tags": {
      "tag_name_1": "tag_value_1",
      "tag_name_2": "tag_value_2"
    },
    "key_only_tags": ["tag3", "tag4"],
    "owners": [
      {
        "name": "change_me",
        "email": "change_me@email.com"
      }
    ]
  },
  "columns": [
    {
      "name": "date_column_name",
      "partition_index": 0,
      "data_type": "date",
      "allow_null": false,
      "format": "%Y/%m/%d"
    },
    {
      "name": "object_column_name",
      "partition_index": null,
      "data_type": "string",
      "allow_null": false
    },
    {
      "name": "int_column_name",
      "partition_index": null,
      "data_type": "integer",
      "allow_null": true
    },
    {
      "name": "bool_column_name",
      "partition_index": null,
      "data_type": "boolean",
      "allow_null": false
    }
  ]
}
```

Once all the values have been set up, just upload the json using the POST `/schema` endpoint of the rAPId instance to create a dataset.

## Auto-generated


Use the POST `/schema/{my_domain_name}/{my_datase_name}/generate` endpoint to automatically generate a draft for the schema.

Consider the following:
- The domain and dataset names will be taken from the url, but can be changed manually afterwards.
- It will not set any [partition columns](#partitions), ensure you add them after the schema has been generated.
- It might not infer the `date` type and its format, ensure you add this information if required.
- It might infer `double` instead of `integer` due to the way pandas works.
- Numbers that are formatted with comma separators should be wrapped in double quotation marks if you wish to retain the commas. If not, remove the commas, and they will be inferred as `integer` or `double`.
- Text that contains commas should be wrapped in double quotation marks.

If we try to get a dataset generated from a csv file `(my_file.csv)` with the following values:

```
date_column_name, object_column_name, int_column_name, bool_column_name
12/10/2021      , "some string"     , 7              , True
21/10/2021      , "a second string" , None           , NA
```

After calling POST `/schema/my_domain_name/my_datase_name/generate` with `my_file.csv` in the body, the generated schema will be:

```json
{
  "metadata": {
    "domain": "my_domain_name",
    "dataset": "my_dataset_name",
    "description": "provide some human readable details about the dataset",
    "sensitivity": "SENSITIVITY",
    "key_value_tags": {},
    "key_only_tags": [],
    "owners": [
      {
        "name": "change_me",
        "email": "change_me@email.com"
      }
    ]
  },
  "columns": [
    {
      "name": "date_column_name",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true,
      "format": null
    },
    {
      "name": "object_column_name",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true,
      "format": null
    },
    {
      "name": "int_column_name",
      "partition_index": null,
      "data_type": "double",
      "allow_null": true,
      "format": null
    },
    {
      "name": "bool_column_name",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true,
      "format": null
    }
  ]
}
```

You might then change the values that fit your data and come with something like:

```json
{
  "metadata": {
    "domain": "changed_domain_name",
    "dataset": "changed_dataset_name",
    "description": "provide some human readable details about the dataset"
    "sensitivity": "SENSITIVITY",
    "key_value_tags": {},
    "key_only_tags": [
      "custom-tag1", "custom-tag2"
    ],
    "owners": [
      {
        "name": "your name",
        "email": "you@gmail.com"
      }
    ]
  },
  "columns": [
    {
      "name": "date_column_name",
      "partition_index": 0,
      "data_type": "date",
      "allow_null": false,
      "format": "%d/%m/%Y"
    },
    {
      "name": "object_column_name",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true
    },
    {
      "name": "int_column_name",
      "partition_index": 1,
      "data_type": "integer",
      "allow_null": false
    },
    {
      "name": "bool_column_name",
      "partition_index": null,
      "data_type": "boolean",
      "allow_null": true
    }
  ]
}
```

Once all the values have been set up, just upload the json using the POST ```/schema``` endpoint of the rAPId instance to create a dataset.
