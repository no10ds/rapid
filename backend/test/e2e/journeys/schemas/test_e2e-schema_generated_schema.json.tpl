{
  "metadata": {
    "layer": "default",
    "domain": "test_e2e",
    "dataset": "{{ name }}",
    "sensitivity": "PUBLIC",
    "description": "",
    "key_value_tags": {},
    "key_only_tags": [],
    "owners": [
      {
        "name": "change_me",
        "email": "change_me@email.com"
      }
    ],
    "update_behaviour": "APPEND",
    "is_latest_version": true
  },
  "columns": [
    {
      "name": "year",
      "data_type": "int",
      "allow_null": true,
      "partition_index": null,
      "format":null,
      "unique": false
    },
    {
      "name": "month",
      "data_type": "int",
      "allow_null": true,
      "partition_index": null,
      "format":null,
      "unique": false
    },
    {
      "name": "destination",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null,
      "format":null,
      "unique": false
    },
    {
      "name": "arrival",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null,
      "format":null,
      "unique": false
    },
    {
      "name": "type",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null,
      "format":null,
      "unique": false
    },
    {
      "name": "status",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null,
      "format":null,
      "unique": false
    }
  ]
}
