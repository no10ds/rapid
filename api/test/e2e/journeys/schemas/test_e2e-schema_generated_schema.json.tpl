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
      "dtype": "int64",
      "nullable": true,
      "unique": false
    },
    "month": {
      "partition_index": null,
      "dtype": "int64",
      "nullable": true,
      "unique": false
    },
    "destination": {
      "partition_index": null,
      "dtype": "object",
      "nullable": true,
      "unique": false
    },
    "arrival": {
      "partition_index": null,
      "dtype": "object",
      "nullable": true,
      "unique": false
    },
    "type": {
      "partition_index": null,
      "dtype": "object",
      "nullable": true,
      "unique": false
    },
    "status": {
      "partition_index": null,
      "dtype": "object",
      "nullable": true,
      "unique": false
    }
  }
}
