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
      "data_type": "int",
      "nullable": true,
      "format": null
    },
    "month": {
      "partition_index": null,
      "data_type": "int",
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
    }
  }
}
