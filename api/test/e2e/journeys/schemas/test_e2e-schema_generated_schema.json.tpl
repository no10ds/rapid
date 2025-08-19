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
