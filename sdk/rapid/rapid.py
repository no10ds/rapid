from datetime import datetime
from typing import Dict, Optional
import json
import time
import requests

import pandas as pd
from pandas import DataFrame

from rapid.auth import RapidAuth
from rapid.items.schema import Schema
from rapid.items.query import Query
from rapid.utils.constants import TIMEOUT_PERIOD
from rapid.exceptions import (
    DataFrameUploadFailedException,
    DataFrameUploadValidationException,
    JobFailedException,
    SchemaGenerationFailedException,
    SchemaCreateFailedException,
    SchemaUpdateFailedException,
    SchemaAlreadyExistsException,
    UnableToFetchJobStatusException,
    DatasetInfoFailedException,
    DatasetNotFoundException,
)


class Rapid:
    def __init__(self, auth: RapidAuth = None) -> None:
        """
        The rAPId class is the main SDK class for the rAPId API. It acts as a wrapper for the various
        API endpoints, providing a simple and intuitive programmatic interface.

        Args:
            auth (:class:`rapid.auth.RapidAuth`, optional): An instance of the rAPId auth class, which is used for authentication and authorization with the API. Defaults to None.
        """
        self.auth = auth if auth else RapidAuth()

    def generate_headers(self) -> Dict:
        return {"Authorization": "Bearer " + self.auth.fetch_token()}

    def list_datasets(self):
        """
        Makes a POST request to the API to list the current datasets.

        Returns:
            A JSON response of the API's response.

        For more details on the response structure, see the API documentation:
        https://getrapid.link/api/docs#/Datasets/list_all_datasets_datasets_post
        """
        response = requests.post(
            f"{self.auth.url}/datasets",
            headers=self.generate_headers(),
            timeout=TIMEOUT_PERIOD,
        )
        return json.loads(response.content.decode("utf-8"))

    def fetch_job_progress(self, _id: str):
        """
        Makes a GET request to the API to fetch the progress of a specific job.

        Args:
            _id (str): The ID of the job to fetch the progress for.

        Returns:
            A JSON response of the API's response.

        For more details on the response structure, see the API documentation:
        https://getrapid.link/api/docs#/Jobs/get_job_jobs__job_id__get
        """
        url = f"{self.auth.url}/jobs/{_id}"
        response = requests.get(
            url, headers=self.generate_headers(), timeout=TIMEOUT_PERIOD
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 200:
            return data
        raise UnableToFetchJobStatusException("Could not check job status", data)

    def wait_for_job_outcome(self, _id: str, interval: int = 1):
        """
        Makes periodic requests to the API to wait for the outcome of a specific job.

        Args:
            _id (str): The ID of the job to wait for the outcome of.
            interval (int, optional): The number of seconds to sleep between requests to the API. Defaults to 1.

        Returns:
            None if the job is successful.

        Raises:
            :class:`rapid.exceptions.JobFailedException`: If the job outcome failed.
        """
        while True:
            progress = self.fetch_job_progress(_id)
            status = progress["status"]
            if status == "SUCCESS":
                return None
            if status == "FAILED":
                raise JobFailedException("Upload failed", progress)
            time.sleep(interval)

    def download_dataframe(
        self,
        domain: str,
        dataset: str,
        version: Optional[int] = None,
        query: Query = Query(),
    ) -> DataFrame:
        """
        Downloads data to a pandas DataFrame based on the domain, dataset and version passed.

        Args:
            domain (str): The domain of the dataset to download the DataFrame from.
            dataset (str): The dataset from the domain to download the DataFrame from.
            version (int, optional): Version of the dataset to download.
            query (:class:`rapid.items.query.Query`, optional): An optional query type to provide when downloading data. Defaults to empty.

        Raises:
            DatasetNotFoundException: :class:`rapid.exceptions.DatasetNotFoundException`: If the
                specificed domain, dataset and version to download does not exist in the rAPId instance
                we throw the dataset not found exception.

        Returns:
            DataFrame: A pandas DataFrame of the data
        """
        url = f"{self.auth.url}/datasets/{domain}/{dataset}/query"
        if version is not None:
            url = f"{url}?version={version}"
        response = requests.post(
            url,
            headers=self.generate_headers(),
            data=json.dumps(query.dict(exclude_none=True)),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 200:
            return pd.read_json(json.dumps(data), orient="index")

        raise DatasetNotFoundException(
            f"Could not find dataset, {domain}/{dataset} to download", data
        )

    def upload_dataframe(
        self, domain: str, dataset: str, df: DataFrame, wait_to_complete: bool = True
    ):
        """
        Uploads a pandas DataFrame to a specified dataset in the API.

        Args:
            domain (str): The domain of the dataset to upload the DataFrame to.
            dataset (str): The name of the dataset to upload the DataFrame to.
            df (DataFrame): The pandas DataFrame to upload.
            wait_to_complete (bool, optional): Whether to wait for the upload job to complete before returning. Defaults to True.

        Raises:
        :class:`rapid.exceptions.DataFrameUploadValidationException`: If the DataFrame's schema is incorrect.
        :class:`rapid.exceptions.DataFrameUploadFailedException`: If an unexpected error occurs while uploading the DataFrame.

        Returns:
            If wait_to_complete is True, returns "Success" if the upload is successful.
            If wait_to_complete is False, returns the ID of the upload job if the upload is accepted.
        """
        url = f"{self.auth.url}/datasets/{domain}/{dataset}"
        response = requests.post(
            url,
            headers=self.generate_headers(),
            files=self.convert_dataframe_for_file_upload(df),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))

        if response.status_code == 202:
            if wait_to_complete:
                self.wait_for_job_outcome(data["details"]["job_id"])
                return "Success"
            return data["details"]["job_id"]
        if response.status_code == 422:
            raise DataFrameUploadValidationException(
                "Could not upload dataframe due to an incorrect schema definition"
            )

        raise DataFrameUploadFailedException(
            "Encountered an unexpected error, could not upload dataframe",
            data["details"],
        )

    def generate_info(self, df: DataFrame, domain: str, dataset: str):
        """
        Generates metadata information for a pandas DataFrame and a specified dataset in the API.

        Args:
            df (DataFrame): The pandas DataFrame to generate metadata for.
            domain (str): The domain of the dataset to generate metadata for.
            dataset (str): The name of the dataset to generate metadata for.

        Raises:
            :class:`rapid.exceptions.DatasetInfoFailedException`: If an error occurs while generating the metadata information.

        Returns:
            A dictionary containing the metadata information for the DataFrame and dataset.
        """
        url = f"{self.auth.url}/datasets/{domain}/{dataset}/info"
        response = requests.post(
            url,
            headers=self.generate_headers(),
            files=self.convert_dataframe_for_file_upload(df),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 200:
            return data

        raise DatasetInfoFailedException(
            "Failed to gather the dataset info", data["details"]
        )

    def convert_dataframe_for_file_upload(self, df: DataFrame):
        """
        Converts a pandas DataFrame to a format that can be used for file uploads to the API.

        Args:
            df (DataFrame): The pandas DataFrame to convert.

        Returns:
            A dictionary containing the converted DataFrame in a format suitable for file uploads to the API.
        """
        return {
            "file": (
                f"rapid-sdk-{int(datetime.now().timestamp())}.csv",
                df.to_csv(index=False),
            )
        }

    def generate_schema(
        self, df: DataFrame, domain: str, dataset: str, sensitivity: str
    ) -> Schema:

        """
        Generates a schema for a pandas DataFrame and a specified dataset in the API.

        Args:
            df (DataFrame): The pandas DataFrame to generate a schema for.
            domain (str): The domain of the dataset to generate a schema for.
            dataset (str): The name of the dataset to generate a schema for.
            sensitivity (str): The sensitivity level of the schema to generate.

        Raises:
            :class:`rapid.exceptions.SchemaGenerationFailedException`: If an error occurs while generating the schema.

        Returns:
            :class:`rapid.items.schema.Schema`: A Schema class type from the generated schema for the DataFrame and dataset.
        """
        url = f"{self.auth.url}/schema/{sensitivity}/{domain}/{dataset}/generate"

        response = requests.post(
            url,
            headers=self.generate_headers(),
            files=self.convert_dataframe_for_file_upload(df),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 200:
            return Schema(**data)
        raise SchemaGenerationFailedException("Could not generate schema", data)

    def create_schema(self, schema: Schema):
        """
        Creates a new schema on the API.

        Args:
            schema (:class:`rapid.items.schema.Schema`): The schema model for which you want to create for.

        Raises:
            :class: `rapid.exceptions.SchemaAlreadyExistsException`: If you try to create a schema that already exists in rAPId.
            :class:`rapid.exceptions.SchemaCreateFailedException`: If an error occurs while trying to update the schema.
        """
        schema_dict = schema.dict()
        url = f"{self.auth.url}/schema"
        response = requests.post(
            url,
            headers=self.generate_headers(),
            data=json.dumps(schema_dict),
            timeout=TIMEOUT_PERIOD,
        )
        if response.status_code == 200:
            pass
        elif response.status_code == 409:
            raise SchemaAlreadyExistsException("The schema already exists")
        else:
            data = json.loads(response.content.decode("utf-8"))
            raise SchemaCreateFailedException("Could not create schema", data)

    def update_schema(self, schema: Schema):
        """
        Uploads a new updated schema to the API.

        Args:
            schema (:class:`rapid.items.schema.Schema`): The new schema model that will be used for the update.

        Raises:
            :class:`rapid.exceptions.SchemaUpdateFailedException`: If an error occurs while trying to update the schema.
        """
        schema_dict = schema.dict()
        url = f"{self.auth.url}/schema"
        response = requests.put(
            url,
            headers=self.generate_headers(),
            data=json.dumps(schema_dict),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 200:
            return data
        raise SchemaUpdateFailedException("Could not update schema", data)
