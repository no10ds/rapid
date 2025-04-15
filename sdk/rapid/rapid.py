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
    ClientDoesNotHaveUserAdminPermissionsException,
    ClientDoesNotHaveDataAdminPermissionsException,
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

    def generate_headers(self, is_file: bool = False) -> Dict:
        return {
            "Authorization": f"Bearer {self.auth.fetch_token()}",
            **({} if is_file else {"Content-Type": "application/json"})
        }
        
    def __perform_api_request(
        self,
        endpoint: str,
        method: str,
        data=None,
        files=None,
        headers={},
        timeout=TIMEOUT_PERIOD,
        success_code=200,
        error_handlers={}
    ):
        """
        A helper method to perform API requests. This method is not intended to be used directly.
        
        Args:
            endpoint (str): The API endpoint to call.
            method (str): The HTTP method to use (GET, POST, PUT, DELETE).
            data (dict, optional): The data to send with the request. Defaults to an empty dictionary.
            files (dict, optional): The files to send with the request. Defaults to None.
            headers (dict, optional): The headers to send with the request. Defaults to an empty dictionary.
            timeout (int, optional): The timeout period for the request. Defaults to TIMEOUT_PERIOD.
            success_code (int, optional): The expected success status code. Defaults to 200.
            error_handlers (dict, optional): A dictionary mapping status codes to exception classes. Defaults to a set of common exceptions.
            
        Returns:
            dict: The JSON response from the API.
        """
        
        if not headers:
            headers = self.generate_headers()
        
        url = f"{self.auth.url}/{endpoint}"
        response = requests.request(
            method,
            url,
            headers=headers,
            params=
            data=json.dumps(data),
            timeout=timeout,
        )
        data = json.loads(response.content.decode("utf-8"))
        if response.status_code == success_code:
            return data
        elif response.status_code in error_handlers:
            raise error_handlers[response.status_code](data)
        elif "default" in error_handlers:
            raise error_handlers["default"](data)
        else:
            raise Exception(
                f"Unexpected error occurred: {response.status_code}", data
            )

    def list_datasets(self):
        """
        List all current datasets within rAPId instance.

        Returns:
            A JSON response of the API's response.
        """
        return self.__perform_api_request(
            endpoint="datasets",
            method="POST",
        )


    def fetch_job_progress(self, _id: str):
        """
        Makes a GET request to the API to fetch the progress of a specific job.

        Args:
            _id (str): The ID of the job to fetch the progress for.

        Returns:
            A JSON response of the API's response.
        """
        
        return self.__perform_api_request(
            endpoint=f"jobs/{_id}",
            method="GET",
            error_handlers={
                "default": lambda d: UnableToFetchJobStatusException("Could not check job status", d),
            },
        )


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
        endpoint = f"datasets/{layer}/{domain}/{dataset}/download"
        if version:
            endpoint += f"?version={version}"
        
        data = self.__perform_api_request(
            endpoint,
            method="POST",
            data=query.dict(exclude_none=True),
            headers=self.generate_headers(),
            success_code=200,
            error_handlers={
                "default": lambda d: DatasetNotFoundException(
                    f"Could not find dataset, {layer}/{domain}/{dataset} to download", d
                ),
            },
        )
        
        return pd.read_json(json.dumps(data), orient="index")
        
    
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
        data = self.__perform_api_request(
            endpoint=f"datasets/{layer}/{domain}/{dataset}",
            method="POST",
            files=self.convert_dataframe_for_file_upload(df),
            headers=self.generate_headers(is_file=True),
            success_code=202,
            error_handlers={
                422: lambda d: DataFrameUploadValidationException("Could not upload dataframe due to an incorrect schema definition", d),
                404: lambda d: DatasetNotFoundException("Could not find dataset", d),
                "default": lambda d: DataFrameUploadFailedException("Encountered an unexpected error, could not upload dataframe", d),
            },
        )
        
        if wait_to_complete:
            self.wait_for_job_outcome(data["details"]["job_id"])
            return "Success"
        
        return data["details"]["job_id"]


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
        return self.__perform_api_request(
            "datasets/{layer}/{domain}/{dataset}/info",
            method="GET",
            error_handlers={
                404: lambda d: DatasetNotFoundException(f"Could not find dataset, {layer}/{domain}/{dataset} to get info", d),
                "default": lambda d: DatasetInfoFailedException("Failed to gather the dataset info", d)
            }
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
        return Schema(**self.__perform_api_request(
            endpoint=f"schema/{layer}/{sensitivity}/{domain}/{dataset}/generate",
            method="POST",
            files=self.convert_dataframe_for_file_upload(df),
            headers=self.generate_headers(is_file=True),
            error_handlers={
                "default": lambda d: SchemaGenerationFailedException("Could not generate schema", d),
            }
        ))

    def create_schema(self, schema: Schema):
        """
        Creates a new schema on the API.

        Args:
            schema rapid.items.schema.Schema: The schema model for which you want to create for.

        Raises:
            rapid.exceptions.SchemaAlreadyExistsException: If you try to create a schema that already exists in rAPId.
            rapid.exceptions.SchemaCreateFailedException: If an error occurs while trying to update the schema.
        """
        return self.__perform_api_request(
            endpoint=f"schema",
            data=json.dumps(schema.dict()),
            method="POST",
            error_handlers={
                404: lambda d: SchemaGenerationFailedException("Could not find schema", d),
                "default": lambda d: SchemaGenerationFailedException("Failed to gather the schema", d)
            }
        )

    def update_schema(self, schema: Schema):
        """
        Uploads a new updated schema to the API.

        Args:
            schema (rapid.items.schema.Schema): The new schema model that will be used for the update.

        Raises:
            rapid.exceptions.SchemaUpdateFailedException: If an error occurs while trying to update the schema.
        """
        return self.__perform_api_request(
            endpoint=f"schema",
            data=json.dumps(schema.dict()),
            method="PUT",
            error_handlers={
                "default": lambda d: SchemaUpdateFailedException("Could not update schema", d)
            }
        )


    def create_client(self, client_name: str, client_permissions: list[str]):
        """
        Creates a new client on the API with the specified permissions.

        Args:
            client_name (str): The name of the client to create.
            client_permissions (list[str]): The permissions of the client to create.

        Raises:
            rapid.exceptions.InvalidPermissionsException: If an error occurs while trying to create the client.
        """
        return self.__perform_api_request(
            endpoint="client",
            method="POST",
            success_code=201,
            data=json.dumps(
                {"client_name": client_name, "permissions": client_permissions}
            ),
            error_handlers={
                400: lambda d: SubjectAlreadyExistsException(f"The client {client_name} already exists"),
                "default": lambda d: InvalidPermissionsException("One or more of the provided permissions is invalid or duplicated")
            }
        )


    def delete_client(self, client_id: str) -> None:
        """
        Deletes a client from the API based on their id

        Args:
            client_id (str): The id of the client to delete.

        Raises:
            rapid.exceptions.SubjectNotFoundException: If the client does not exist.
        """
        return self.__perform_api_request(
            endpoint=f"client/{client_id}",
            method="DELETE",
            error_handlers={
                "default": lambda d: SubjectNotFoundException(f"Failed to delete client with id: {client_id}, ensure it exists.")
            }
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
        return self.__perform_api_request(
            endpoint=f"subject/permissions",
            method="PUT",
            data=json.dumps({"subject_id": subject_id, "permissions": permissions}),
            error_handlers={
                "default": lambda d: InvalidPermissionsException("One or more of the provided permissions is invalid or duplicated")
            }
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
        return self.__perform_api_request(
            endpoint=f"protected_domains/{name}",
            method="POST",
            success_code=201,
            error_handlers={
                400: lambda d: InvalidDomainNameException(d["details"]),
                409: lambda d: DomainConflictException(d["details"]),
                "default": lambda d: Exception("Failed to create protected domain")
            }
        )


    def create_user(self, user_name: str, user_email: str, user_permissions: list[str]):
        """
        Creates a new user on the API with the specified permissions.

        Args:
            user_name (str): The name of the user to create.
            user_email (str): The email of the user to create.
            user_permissions (list[str]): The permissions of the user to create.

        Raises:
            rapid.exceptions.InvalidPermissionsException: If an error occurs while trying to create the user.
        """

        return self.__perform_api_request(
            endpoint="user",
            method="POST",
            success_code=201,
            data=json.dumps(
                {
                    "username": user_name,
                    "email": user_email,
                    "permissions": user_permissions,
                }
            ),
            error_handlers={
                400: lambda d: SubjectAlreadyExistsException(d["details"]) if d["details"] != invalid_perm_msg else InvalidPermissionsException(d["details"]),
                401: lambda d: ClientDoesNotHaveUserAdminPermissionsException(d["details"]),
                "default": lambda d: Exception("Failed to create user")
            }
        )


    def delete_user(self, user_name: str, user_id: str):
        """
        Deletes a client from the API based on their id

        Args:
            client_id (str): The id of the client to delete.

        Raises:
            rapid.exceptions.SubjectNotFoundException: If the client does not exist.
        """
        return self.__perform_api_request(
            endpoint="user",
            method="DELETE",
            data=json.dumps({"username": user_name, "user_id": user_id}),
            error_handlers={
                400: lambda d: SubjectNotFoundException(f"Failed to delete user with id: {user_id}, ensure it exists."),
                401: lambda d: ClientDoesNotHaveUserAdminPermissionsException(d["details"]),
                "default": lambda d: Exception("Failed to delete user")
            }
        )


    def list_subjects(self):
        """
        List all current subjects within rAPId instance.

        Returns:
            A JSON response of the API's response.
        """
        return self.__perform_api_request(
            endpoint="subjects",
            method="GET",
            error_handlers={
                401: lambda d: ClientDoesNotHaveUserAdminPermissionsException(d["details"]),
                "default": lambda d: Exception("Failed to list subjects")
            }
        )


    def list_layers(self):
        """
        List all current layers within rAPId instance.

        Returns:
            A JSON response of the API's response.
        """
        return self.__perform_api_request(
            endpoint="layers",
            method="GET",
            error_handlers={
                401: lambda d: ClientDoesNotHaveUserAdminPermissionsException(d["details"]),
                "default": lambda d: Exception("Failed to list layers")
            }
        )


    def list_protected_domains(self):
        """
        List all current protected domains within rAPId instance.

        Returns:
            A JSON response of the API's response.
        """
        return self.__perform_api_request(
            endpoint="protected_domains",
            method="GET",
            error_handlers={
                401: lambda d: ClientDoesNotHaveUserAdminPermissionsException(d["details"]),
                "default": lambda d: Exception("Failed to list protected domains")
            }
        )

    def delete_dataset(self, layer: str, domain: str, dataset: str):
        """
        Deletes a dataset from the API based on their id

        Args:
            layer (str): The dataset layer to delete.
            domain (str): The dataset domain to delete.
            dataset (str): The dataset to delete.

        Raises:
            rapid.exceptions.DatasetNotFoundException: If the dataset does not exist.
        """
        return self.__perform_api_request(
            endpoint=f"datasets/{layer}/{domain}/{dataset}",
            method="DELETE",
            error_handlers={
                400: lambda d: DatasetNotFoundException(f"Could not find dataset, {layer}/{domain}/{dataset} to delete", d),
                401: lambda d: ClientDoesNotHaveDataAdminPermissionsException(d["details"]),
                "default": lambda d: Exception("Failed to delete dataset")
            }
        )
