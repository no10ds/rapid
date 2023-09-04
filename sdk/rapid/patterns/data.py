from typing import Union, List
from pandas import DataFrame
from rapid.exceptions import (
    ColumnNotDifferentException,
    DataFrameUploadValidationException,
)
from rapid.items.schema import Schema, SchemaMetadata, Column
from rapid import Rapid


def upload_and_create_dataframe(
    rapid: Rapid, metadata: SchemaMetadata, df: DataFrame, upgrade_schema_on_fail=False
):
    """
    Generates a schema and dataset from a pandas Dataframe. The function first creates the schema
    using the API and the uploads the DataFrame to this schema, uploading the data to rAPId.

    Args:
        rapid (Rapid): An instance of the rAPId SDK's main class.
        metadata (SchemaMetadata): The metadata for the schema to be created and the dataset to upload the DataFrame to.ß
        df (DataFrame): The pandas DataFrame to generate a schema for and upload to the dataset.
        upgrade_schema_on_fail (bool, optional): Whether to upgrade the schema if the DataFrame's schema is incorrect. Defaults to False.

    Raises:
        rapid.exceptions.DataFrameUploadValidationException: If the DataFrame's schema is incorrect and upgrade_schema_on_fail is False.
        Exception: If an error occurs while generating the schema, creating the schema, or uploading the DataFrame.
    """
    schema = rapid.generate_schema(
        df, metadata.layer, metadata.domain, metadata.dataset, metadata.sensitivity
    )
    try:
        rapid.create_schema(schema)
        rapid.upload_dataframe(metadata.layer, metadata.domain, metadata.dataset, df)
    except DataFrameUploadValidationException as exception:
        if upgrade_schema_on_fail:
            update_schema_dataframe(rapid, metadata, df, schema.columns)
        else:
            raise exception
    except Exception as exception:
        raise exception


def update_schema_dataframe(
    rapid: Rapid,
    metadata: SchemaMetadata,
    df: DataFrame,
    new_columns: Union[List[Column], List[dict]],
):
    """
    Updates a schema for a specified dataset in the API based on a pandas DataFrame.

    Args:
        rapid (Rapid): An instance of the rAPId SDK's main class.
        metadata (SchemaMetadata): The metadata for the schema to be updated and the dataset the DataFrame belongs to.
        df (DataFrame): The pandas DataFrame to generate the original schema columns from.
        new_columns (Union[List[Column], List[dict]]): The new schema columns to update the schema with.

    Raises:
        rapid.exceptions.ColumnNotDifferentException: If the new schema columns are the same as the existing schema columns.
        Exception: If an error occurs while generating the schema information, updating the schema, or comparing the schema columns.
    """
    info = rapid.generate_info(df, metadata.layer, metadata.domain, metadata.dataset)
    try:
        schema = Schema(metadata=metadata, columns=info["columns"])
        if schema.are_columns_the_same(new_columns=new_columns):
            raise ColumnNotDifferentException

        schema.columns = new_columns
        rapid.update_schema(schema)
    except Exception as e:
        raise e
