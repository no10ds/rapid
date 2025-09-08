{
  "metadata": {
    "layer": "default",
    "domain": "test_e2e_protected",
    "dataset": "{{name}}",
    "sensitivity": "PROTECTED",
    "description": "A test dataset",
    "key_value_tags": {},
    "key_only_tags": [],
    "owners": [
      {
        "name": "test_e2e_protected",
        "email": "test_e2e_protected@email.com"
      }
    ],
    "tags": {},
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
