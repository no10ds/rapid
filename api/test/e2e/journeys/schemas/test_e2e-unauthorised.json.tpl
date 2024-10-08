{
  "metadata": {
    "layer": "default",
    "domain": "test_e2e",
    "dataset": "{{name}}",
    "sensitivity": "PUBLIC",
    "description": "A test dataset",
    "tags": {
      "test_e2e": "unauthorised",
      "test": "e2e"
    },
    "owners": [
      {
        "name": "unauthorised",
        "email": "unauthorised@test.com"
      }
    ],
    "update_behaviour": "OVERWRITE"
  },
  "columns": [
    {
      "name": "year",
      "partition_index": null,
      "data_type": "int",
      "allow_null": true,
      "format": null
    },
    {
      "name": "month",
      "partition_index": null,
      "data_type": "int",
      "allow_null": true,
      "format": null
    },
    {
      "name": "destination",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true,
      "format": null
    },
    {
      "name": "arrival",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true,
      "format": null
    },
    {
      "name": "type",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true,
      "format": null
    },
    {
      "name": "status",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true,
      "format": null
    }
  ]
}
