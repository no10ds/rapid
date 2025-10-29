{
  "metadata": {
    "layer": "default",
    "domain": "test_e2e",
    "dataset": "{{ name }}",
    "sensitivity": "PUBLIC",
    "description": "A test dataset with custom pandera checks",
    "tags": {
      "test_e2e": "custom_checks",
      "test": "validation"
    },
    "owners": [
      {
        "name": "test",
        "email": "test@example.com"
      }
    ],
    "update_behaviour": "APPEND"
  },
  "columns": [
    {
      "name": "year",
      "partition_index": null,
      "data_type": "int",
      "allow_null": false,
      "format": null,
      "checks": {
        "year_range_check": {
          "check_type": "in_range",
          "parameters": {"min_value": 2000, "max_value": 2030},
          "error": "Year must be between 2000 and 2030"
        }
      }
    },
    {
      "name": "month",
      "partition_index": null,
      "data_type": "int",
      "allow_null": false,
      "format": null,
      "checks": {
        "month_range_check": {
          "check_type": "isin",
          "parameters": {"allowed_values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
          "error": "Month must be between 1 and 12"
        }
      }
    },
    {
      "name": "destination",
      "partition_index": null,
      "data_type": "string",
      "allow_null": false,
      "format": null
    },
    {
      "name": "arrival",
      "partition_index": null,
      "data_type": "string",
      "allow_null": false,
      "format": null
    },
    {
      "name": "type",
      "partition_index": null,
      "data_type": "string",
      "allow_null": false,
      "format": null,
      "checks": {
        "type_check": {
          "check_type": "isin",
          "parameters": {"allowed_values": ["regular", "express", "priority"]},
          "error": "Type must be one of: regular, express, priority"
        }
      }
    },
    {
      "name": "status",
      "partition_index": null,
      "data_type": "string",
      "allow_null": false,
      "format": null,
      "checks": {
        "status_check": {
          "check_type": "isin",
          "parameters": {"allowed_values": ["completed", "pending", "cancelled"]},
          "error": "Status must be one of: completed, pending, cancelled"
        }
      }
    }
  ]
}
