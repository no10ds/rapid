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
  "columns": {
    "year": {
      "partition_index": null,
      "dtype": "int",
      "nullable": true,
      "format": null
    },
    "month": {
      "partition_index": null,
      "dtype": "int",
      "nullable": true,
      "format": null
    },
    "destination": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
      "format": null
    },
    "arrival": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
      "format": null
    },
    "type": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
      "format": null
    },
    "status": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
      "format": null
    }
  }
}
