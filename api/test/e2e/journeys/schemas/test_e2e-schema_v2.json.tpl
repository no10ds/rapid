{
  "metadata": {
    "layer": "default",
    "domain": "test_e2e",
    "dataset": "{{ name }}",
    "sensitivity": "PUBLIC",
    "description": "A test dataset",
    "tags": {
      "test_e2e": "upload",
      "test": "e2e",
      "new_tag": "should not be created"
    },
    "owners": [
      {
        "name": "upload",
        "email": "upload1@test.com"
      }
    ],
    "update_behaviour": "OVERWRITE"
  },
  "columns": [
    {
      "name": "year",
      "partition_index": null,
      "data_type": "int",
      "allow_null": true
    },
    {
      "name": "month",
      "partition_index": null,
      "data_type": "double",
      "allow_null": true
    },
    {
      "name": "destination",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true
    },
    {
      "name": "arrival",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true
    },
    {
      "name": "type",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true
    },
    {
      "name": "status",
      "partition_index": null,
      "data_type": "string",
      "allow_null": true
    },
    {
      "name": "newcolumn",
      "partition_index": null,
      "data_type": "int",
      "allow_null": true
    }
  ]
}
