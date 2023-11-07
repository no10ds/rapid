from pandas import DataFrame
from rapid.exceptions import (
    DataFrameUploadValidationException,
    DatasetNotFoundException,
)
from rapid.items.schema import Schema, SchemaMetadata
from rapid import Rapid


def upload_and_create_dataset(
    rapid: Rapid, metadata: SchemaMetadata, df: DataFrame, upgrade_schema_on_fail=False
):
    """
    Uploads a dataframe to a dataset in the API, creating schema first if necessary.

    Args:
        rapid (Rapid): An instance of the rAPId SDK's main class.
        metadata (SchemaMetadata): The metadata for the schema to be created and the dataset to upload the DataFrame to.ß
        df (DataFrame): The pandas DataFrame to generate a schema for and upload to the dataset.
        upgrade_schema_on_fail (bool, optional): Whether to upgrade the schema if the DataFrame's schema is incorrect. Defaults to False.

    Raises:
        rapid.exceptions.DataFrameUploadValidationException: If the DataFrame's schema is incorrect and upgrade_schema_on_fail is False.
    """
    try:
        rapid.upload_dataframe(
            metadata.layer, metadata.domain, metadata.dataset, df, wait_to_complete=True
        )
    except DatasetNotFoundException:
        schema = rapid.generate_schema(
            df, metadata.layer, metadata.domain, metadata.dataset, metadata.sensitivity
        )
        schema.metadata = metadata
        rapid.create_schema(schema)
        rapid.upload_dataframe(
            metadata.layer, metadata.domain, metadata.dataset, df, wait_to_complete=True
        )
    except DataFrameUploadValidationException as validation_exception:
        if upgrade_schema_on_fail:
            update_schema_to_dataframe(rapid, metadata, df)
            rapid.upload_dataframe(
                metadata.layer,
                metadata.domain,
                metadata.dataset,
                df,
                wait_to_complete=True,
            )
        else:
            raise validation_exception


def update_schema_to_dataframe(
    rapid: Rapid,
    metadata: SchemaMetadata,
    df: DataFrame,
):
    """
    Updates a schema for a specified dataset in the API to match the given Dataframe.

    Args:
        rapid (Rapid): An instance of the rAPId SDK's main class.
        metadata (SchemaMetadata): The metadata for the schema to be updated and the dataset the DataFrame belongs to.
        df (Dataframe): The dataframe that the schema should be updated to match.
    """
    schema_response = rapid.generate_schema(
        df, metadata.layer, metadata.domain, metadata.dataset, metadata.sensitivity
    )
    schema = Schema(metadata=metadata, columns=schema_response.columns)
    rapid.update_schema(schema)
