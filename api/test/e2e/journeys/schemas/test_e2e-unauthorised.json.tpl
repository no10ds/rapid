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
    },
    "month": {
      "partition_index": null,
      "dtype": "int",
      "nullable": true,
    },
    "destination": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
    },
    "arrival": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
    },
    "type": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
    },
    "status": {
      "partition_index": null,
      "dtype": "string",
      "nullable": true,
    }
  }
}
