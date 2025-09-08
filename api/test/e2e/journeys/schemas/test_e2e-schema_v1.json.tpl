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
