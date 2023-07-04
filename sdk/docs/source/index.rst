=====================================
rAPId-sdk
=====================================

The rAPId-sdk is a lightweight Python wrapper for 10 Downing Street's `rAPId api project <https://github.com/no10ds/rapid-api>`_.
rAPId aims to create a consistent, secure, interoperable data storage and sharing interfaces (APIs).

The sdk is a standalone Python library that can provide easy programmatic access to the core rAPId functionality. It can handle
programmatic schema creation and updation using modern Python classes and data structures.

Installation
============

Install the sdk easily with `pip`::

   $ pip install rapid-sdk

How to Use
==========

Once installed into your project the first thing you will want to do is create an instance of the rAPId class.

In order for your code to connect to rAPId you will need your rAPId `client_id`, `client_secret` and `url` values. By default the
authentication module will try and read these from your environment variables as `RAPID_CLIENT_ID`, `RAPID_CLIENT_SECRET` and `RAPID_URL`
respectively. Alternatively you can create your own instance of the rAPId authentication class::

   from rapid import Rapid
   from rapid import RapidAuth

   rapid_authentication = RapidAuth()
   rapid = Rapid(auth=rapid_authentication)

If you do not want to use environment variables (however this is discouraged as secrets should always be kept safe), you can pass the
values directly to the class as follows.::

   rapid_authentication = RapidAuth(
      client_id=os.getenv("RAPID_CLIENT_ID"),
      client_secret=os.getenv("RAPID_CLIENT_SECRET"),
      url=os.getenv("RAPID_URL")
   )

Generate Schema
---------------

The sdk provides an easy and intuitive way to generate a schema based on a Pandas DataFrame you might have. The function returns
a custom Pydantic Schema class type that matches a valid rAPId schema. This can be used to programmatic information of the schema
such as domain, dataset and lists of it's columns::

   import pandas as pd
   from rapid import Rapid

   rapid = Rapid()

   raw_data = [
      {"a": 1, "b": 2, "c": 3},
      {"a": 10, "b": 20, "c": 30}
   ]
   df = pd.DataFrame(raw_data)

   schema = rapid.generate_schema(
      df=df,
      domain="domain",
      dataset="dataset",
      sensitivity="PUBLIC"
   )

   print("Domain ", schema.metadata.domain)
   print("Columns ", schema.columns.dict())

Download Data
-------------

The sdk provides an easy way to automatically download a specific dataset based on an optional version and query. The function returns
the data in a pandas DataFrame format. See the example below for a basic example::

      import pandas as pd
      from rapid import Rapid

      data = rapid.download_dataframe(
         domain="domain",
         dataset="dataset",
         version=1
      )

      print(data.info())

It is possible to pass a query to get more granular information about a dataset. We provide a Pydantic query class that can get passed
into the download function. For more information on writing rAPId compatiable queries see `the documentation <https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/usage.md#how-to-construct-a-query-object>`_
and the example::

   import pandas as pd
   from rapid import Rapid
   from rapid.items.query import Query

   query = Query(
      select_columns=["column_to_select_one", "column_to_select_two"],
      limit="100"
   )

   data = rapid.download_dataframe(
      domain="domain",
      dataset="dataset",
      verson=1,
      query=query
   )

   print(data.info())


API Documentation
=================

.. toctree::
   :maxdepth: 2
   :glob:

   api/rapid
   api/auth
   api/items
   api/patterns

Useful Patterns
===============
With the sdk we ship useful functions that handle common programmatic functionality for rAPId.

Below is an simple example for uploading a Pandas DataFrame to the API::

   import pandas as pd
   from rapid import Rapid
   from rapid.patterns import data
   from rapid.items.schema import SchemaMetadata, SensitivityLevel, Owner
   from rapid.exceptions import DataFrameUploadValidationException

   rapid = Rapid()

   raw_data = [
      {"a": 1, "b": 2, "c": 3},
      {"a": 10, "b": 20, "c": 30}
   ]
   df = pd.DataFrame(raw_data)

   metadata = SchemaMetadata(
    domain='mydomain',
    dataset='mydataset',
    owners=[Owner(name="myname", email="myemail@email.com")],
    sensitivity=SensitivityLevel.PUBLIC.value
   )

   try:
      data.upload_and_create_dataframe(
         rapid=rapid,
         df=df,
         metadata=metadata,
         upgrade_schema_on_fail=False
      )
   except DataFrameUploadValidationException:
      print('Incorrect DataFrame schema')

Now going forward say for instance we now expect that for column c we can expect some values
to be floating points, we want to update the schema::

   import pandas as pd
   from rapid import Rapid
   from rapid.patterns import data
   from rapid.items.schema import SchemaMetadata, SensitivityLevel, Owner, Column
   from rapid.exceptions import ColumnNotDifferentException

   rapid = Rapid()

   raw_data = [
      {"a": 1, "b": 2, "c": 3},
      {"a": 10, "b": 20, "c": 30}
   ]
   df = pd.DataFrame(raw_data)

   metadata = SchemaMetadata(
    domain='mydomain',
    dataset='mydataset',
    owners=[Owner(name="myname", email="myemail@email.com")],
    _sensitivity=SensitivityLevel.PUBLIC.value
   )

   try:
      data.update_schema_dataframe(
         rapid=rapid,
         df=df,
         metadata=metadata,
         new_columns=[
            Column(
               name="c",
               data_type="Float64"
            )
         ]
      )
   except ColumnNotDifferentException:
      print('Columns not different.')

Search
======
* :ref:`search`
