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
  "columns": {
    "year": {
      "partition_index": null,
      "data_type": "int",
      "nullable": true,
      "format": null
    },
    "month": {
      "partition_index": null,
      "data_type": "double",
      "nullable": true,
      "format": null
    },
    "destination": {
      "partition_index": null,
      "data_type": "string",
      "nullable": true,
      "format": null
    },
    "arrival": {
      "partition_index": null,
      "data_type": "string",
      "nullable": true,
      "format": null
    },
    "type": {
      "partition_index": null,
      "data_type": "string",
      "nullable": true,
      "format": null
    },
    "status": {
      "partition_index": null,
      "data_type": "string",
      "nullable": true,
      "format": null
    },
    "newcolumn": {
      "partition_index": null,
      "data_type": "int",
      "nullable": true,
      "format": null
    }
  }
}
