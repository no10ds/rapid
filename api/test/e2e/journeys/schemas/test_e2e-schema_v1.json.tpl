{
  "metadata": {
    "layer": "default",
    "domain": "test_e2e",
    "dataset": "{{ name }}",
    "sensitivity": "PUBLIC",
    "description": "A test dataset",
    "key_value_tags": {
      "test_e2e": "update",
      "test": "e2e"
    },
    "key_only_tags": [],
    "owners": [
      {
        "name": "update",
        "email": "update@email.com"
      }
    ],
    "update_behaviour": "APPEND"
  },
  "columns": [
    {
      "name": "year",
      "data_type": "int",
      "allow_null": true,
      "partition_index": null
    },
    {
      "name": "month",
      "data_type": "int",
      "allow_null": true,
      "partition_index": null
    },
    {
      "name": "destination",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null
    },
    {
      "name": "arrival",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null
    },
    {
      "name": "type",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null
    },
    {
      "name": "status",
      "data_type": "string",
      "allow_null": true,
      "partition_index": null
    }
  ]
}
