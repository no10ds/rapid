The sdk is a standalone Python library that can provide easy programmatic access to the core rAPId functionality. It can handle programmatic schema creation and updating using modern Python classes and data structures.

## Installation

Install the sdk easily with pip:

```
pip install rapid-sdk
```

### How to Use

Once installed into your project the first thing you will want to do is create an instance of the rAPId class.

In order for your code to connect to rAPId you will need your rAPId client_id, client_secret and url values. By default the authentication module will try and read these from your environment variables as `RAPID_CLIENT_ID`, `RAPID_CLIENT_SECRET` and `RAPID_URL` respectively. Alternatively you can create your own instance of the rAPId authentication class.

```python
from rapid import Rapid
from rapid import RapidAuth

rapid_authentication = RapidAuth()
rapid = Rapid(auth=rapid_authentication)
```

Alternatively, you can pass the values directly to the RapidAuth class:

```python
rapid_authentication = RapidAuth(
    client_id="your_client_id",
    client_secret="your_client_secret",
    url="https://your-rapid-instance.com"
)
rapid = Rapid(auth=rapid_authentication)
```

> Note: For security, it's recommended to use environment variables rather than hardcoding credentials in your code.

### Generate Schema

The sdk provides an easy and intuitive way to generate a schema based on a Pandas DataFrame you might have. The function returns a custom Pydantic Schema class type that matches a valid rAPId schema. This can be used to programmatically access information about the schema such as domain, dataset and lists of columns.

```python
import pandas as pd
from rapid import Rapid

rapid = Rapid()

raw_data = [{"a": 1, "b": 2, "c": 3}, {"a": 10, "b": 20, "c": 30}]
df = pd.DataFrame(raw_data)

schema = rapid.generate_schema(
    df=df, layer="default", domain="domain", dataset="dataset", sensitivity="PUBLIC"
)

print("Domain ", schema.metadata.domain)
print("Columns ", [col.model_dump() for col in schema.columns])
```

### Upload Schema

You can upload a generated schema via the sdk.

```
rapid.create_schema(schema)
```

> Note: Uploading a schema requires `DATA_ADMIN` permissions.

### Download Data

The sdk provides an easy way to automatically download a specific dataset based on an optional version and query. The function returns the data in a pandas DataFrame format. See the example below for a basic example.

```python
import pandas as pd
from rapid import Rapid

data = rapid.download_dataframe(
    layer="default", domain="domain", dataset="dataset", version=1
)

print(data.info())
```

It is possible to pass a query to get more granular information about a dataset. We provide a Pydantic query class that can get passed into the download function. For more information on writing rAPId compatible queries see [the query documentation](../api/query.md) and the example below.

```python
import pandas as pd
from rapid import Rapid
from rapid.items.query import Query

query = Query(
    select_columns=["column_to_select_one", "column_to_select_two"], limit="100"
)

data = rapid.download_dataframe(
    layer="default", domain="domain", dataset="dataset", version=1, query=query
)

print(data.info())
```
