import json
import time
import requests

from datetime import datetime
from typing import Dict, Optional

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
    InvalidPermissionsException,
    SubjectAlreadyExistsException,
    SubjectNotFoundException,
    InvalidDomainNameException,
    DomainConflictException,
)


class Rapid:
    def __init__(self, auth: RapidAuth = None) -> None:
        """
        The rAPId class is the main SDK class for the rAPId API. It acts as a wrapper for the various
        API endpoints, providing a simple and intuitive programmatic interface.

        Args:
            auth (int, optional): An instance of the rAPId auth class, which is used for authentication and authorization with the API. Defaults to None.
        """
        self.auth = auth if auth else RapidAuth()

    def generate_headers(self) -> Dict:
        return {"Authorization": "Bearer " + self.auth.fetch_token()}

    def list_datasets(self):
        """
        List all current datasets within rAPId instance.

        Returns:
            A JSON response of the API's response.
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
            rapid.exceptions.JobFailedException: If the job outcome failed.
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
        layer: str,
        domain: str,
        dataset: str,
        version: Optional[int] = None,
        query: Query = Query(),
    ) -> DataFrame:
        """
        Downloads data to a pandas DataFrame based on the domain, dataset and version passed.

        Args:
            layer (str): The layer of the dataset to download the DataFrame from.
            domain (str): The domain of the dataset to download the DataFrame from.
            dataset (str): The dataset from the domain to download the DataFrame from.
            version (int, optional): Version of the dataset to download.
            query (rapid.items.query.Query, optional): An optional query type to provide when downloading data. Defaults to empty.

        Raises:
            DatasetNotFoundException: rapid.exceptions.DatasetNotFoundException: If the
                specificed domain, dataset and version to download does not exist in the rAPId instance
                we throw the dataset not found exception.

        Returns:
            DataFrame: A pandas DataFrame of the data
        """
        url = f"{self.auth.url}/datasets/{layer}/{domain}/{dataset}/query"
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
            f"Could not find dataset, {layer}/{domain}/{dataset} to download", data
        )

    def upload_dataframe(
        self,
        layer: str,
        domain: str,
        dataset: str,
        df: DataFrame,
        wait_to_complete: bool = True,
    ):
        """
        Uploads a pandas DataFrame to a specified dataset in the API.

        Args:
            layer (str): The layer of the dataset to upload the DataFrame to.
            domain (str): The domain of the dataset to upload the DataFrame to.
            dataset (str): The name of the dataset to upload the DataFrame to.
            df (DataFrame): The pandas DataFrame to upload.
            wait_to_complete (bool, optional): Whether to wait for the upload job to complete before returning. Defaults to True.

        Raises:
            rapid.exceptions.DataFrameUploadValidationException: If the DataFrame's schema is incorrect.
            rapid.exceptions.DataFrameUploadFailedException: If an unexpected error occurs while uploading the DataFrame.
            rapid.exceptions.DatasetNotFoundException: If the specified dataset does not exist.

        Returns:
            If wait_to_complete is True, returns "Success" if the upload is successful.
            If wait_to_complete is False, returns the ID of the upload job if the upload is accepted.
        """
        url = f"{self.auth.url}/datasets/{layer}/{domain}/{dataset}"
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
        elif response.status_code == 404:
            raise DatasetNotFoundException(
                "Could not find dataset: {layer}/{domain}/{dataset}", data
            )
        else:
            raise DataFrameUploadFailedException(
                "Encountered an unexpected error, could not upload dataframe",
                data["details"],
            )

    def fetch_dataset_info(self, layer: str, domain: str, dataset: str):
        """
        Fetches information about the specified dataset in the API.

        Args:
            layer (str): The layer of the dataset to fetch metadata for.
            domain (str): The domain of the dataset to fetch metadata for.
            dataset (str): The name of the dataset to fetch metadata for.

        Raises:
            rapid.exceptions.DatasetInfoFailedException: If an error occurs while fetching the dataset information.
            rapid.exceptions.DatasetNotFoundException: If the specified dataset does not exist.

        Returns:
            A dictionary containing the metadata information for the dataset.
        """
        url = f"{self.auth.url}/datasets/{layer}/{domain}/{dataset}/info"
        response = requests.get(
            url,
            headers=self.generate_headers(),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 200:
            return data

        if response.status_code == 404:
            raise DatasetNotFoundException(
                f"Could not find dataset, {layer}/{domain}/{dataset} to get info", data
            )

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
                f"rapid-sdk-{int(datetime.now().timestamp())}.parquet",
                df.to_parquet(index=False),
            )
        }

    def generate_schema(
        self, df: DataFrame, layer: str, domain: str, dataset: str, sensitivity: str
    ) -> Schema:
        """
        Generates a schema for a pandas DataFrame and a specified dataset in the API.

        Args:
            df (DataFrame): The pandas DataFrame to generate a schema for.
            layer (str): The layer of the dataset to generate a schema for.
            domain (str): The domain of the dataset to generate a schema for.
            dataset (str): The name of the dataset to generate a schema for.
            sensitivity (str): The sensitivity level of the schema to generate.

        Raises:
            rapid.exceptions.SchemaGenerationFailedException: If an error occurs while generating the schema.

        Returns:
            rapid.items.schema.Schema: A Schema class type from the generated schema for the DataFrame and dataset.
        """
        url = (
            f"{self.auth.url}/schema/{layer}/{sensitivity}/{domain}/{dataset}/generate"
        )

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
            schema rapid.items.schema.Schema: The schema model for which you want to create for.

        Raises:
            rapid.exceptions.SchemaAlreadyExistsException: If you try to create a schema that already exists in rAPId.
            rapid.exceptions.SchemaCreateFailedException: If an error occurs while trying to update the schema.
        """
        schema_dict = schema.dict()
        url = f"{self.auth.url}/schema"
        response = requests.post(
            url,
            headers=self.generate_headers(),
            data=json.dumps(schema_dict),
            timeout=TIMEOUT_PERIOD,
        )
        if response.status_code == 201:
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
            schema (rapid.items.schema.Schema): The new schema model that will be used for the update.

        Raises:
            rapid.exceptions.SchemaUpdateFailedException: If an error occurs while trying to update the schema.
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

    def create_client(self, client_name: str, client_permissions: list[str]):
        """
        Creates a new client on the API with the specified permissions.

        Args:
            client_name (str): The name of the client to create.
            client_permissions (list[str]): The permissions of the client to create.

        Raises:
            rapid.exceptions.InvalidPermissionsException: If an error occurs while trying to create the client.
        """
        url = f"{self.auth.url}/client"
        response = requests.post(
            url,
            headers=self.generate_headers(),
            data=json.dumps(
                {"client_name": client_name, "permissions": client_permissions}
            ),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 201:
            return data
        elif response.status_code == 400:
            raise SubjectAlreadyExistsException(
                f"The client {client_name} already exists"
            )
        raise InvalidPermissionsException(
            "One or more of the provided permissions is invalid or duplicated"
        )

    def delete_client(self, client_id: str) -> None:
        """
        Deletes a client from the API based on their id

        Args:
            client_id (str): The id of the client to delete.

        Raises:
            rapid.exceptions.SubjectNotFoundException: If the client does not exist.
        """
        url = f"{self.auth.url}/client/{client_id}"
        response = requests.delete(
            url,
            headers=self.generate_headers(),
            timeout=TIMEOUT_PERIOD,
        )
        if response.status_code == 200:
            return None

        raise SubjectNotFoundException(
            f"Failed to delete client with id: {client_id}, ensure it exists."
        )

    def update_subject_permissions(self, subject_id: str, permissions: list[str]):
        """
        Updates the permissions of a subject on the API.

        Args:
            subject_id (str): The id of the subject to update.
            permissions (list[str]): The permissions to update the subject with.

        Raises:
            rapid.exceptions.InvalidPermissionsException: If an error occurs while trying to create the client.
        """
        url = f"{self.auth.url}/subject/permissions"
        response = requests.put(
            url,
            headers=self.generate_headers(),
            data=json.dumps({"subject_id": subject_id, "permissions": permissions}),
            timeout=TIMEOUT_PERIOD,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 200:
            return data

        raise InvalidPermissionsException(
            "One or more of the provided permissions is invalid or duplicated"
        )

    def create_protected_domain(self, name: str):
        """
        Creates a new protected domain.

        Args:
            name (str): The name of the protected domain to create.

        Raises:
            rapid.exceptions.InvalidDomainNameException: If the domain name is invalid.
            rapid.exceptions.DomainConflictException: If the domain already exists.

        """
        url = f"{self.auth.url}/protected_domains/{name}"
        response = requests.post(
            url, headers=self.generate_headers(), timeout=TIMEOUT_PERIOD
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == 201:
            return
        elif response.status_code == 400:
            raise InvalidDomainNameException(data["details"])
        elif response.status_code == 409:
            raise DomainConflictException(data["details"])

        raise Exception("Failed to create protected domain")
