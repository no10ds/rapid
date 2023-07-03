import os
import tempfile
from pathlib import Path

from fastapi import UploadFile
from unittest.mock import patch, Mock
from pandas.util.testing import assert_frame_equal

import pandas as pd

from api.common.config.constants import CONTENT_ENCODING
from api.common.data_handlers import (
    CHUNK_SIZE,
    construct_chunked_dataframe,
    store_file_to_disk,
    store_csv_file_to_disk,
)


class TestStoreFileToDisk:
    @patch("api.common.data_handlers.store_csv_file_to_disk")
    def test_store_file_to_disk_csv_file(self, mock_store_csv_file_to_disk):
        mock_file = UploadFile(filename="test.csv", file=None)
        extension = "csv"
        id = "xxx-yyy"
        store_file_to_disk(extension, id, mock_file)

        path = Path("xxx-yyy-test.csv")
        mock_store_csv_file_to_disk.assert_called_once_with(path, False, mock_file)

    @patch("api.common.data_handlers.store_csv_file_to_disk")
    def test_store_file_to_disk_csv_file_chunked(self, mock_store_csv_file_to_disk):
        mock_file = UploadFile(filename="test.csv", file=None)
        extension = "csv"
        id = "xxx-yyy"
        to_chunk = True
        store_file_to_disk(extension, id, mock_file, to_chunk)

        path = Path("xxx-yyy-test.csv")
        mock_store_csv_file_to_disk.assert_called_once_with(path, True, mock_file)

    @patch("api.common.data_handlers.store_parquet_file_to_disk")
    def test_store_file_to_disk_parquet(self, mock_store_parquet_file_to_disk):
        mock_file = UploadFile(filename="test.parquet", file=None)
        extension = "parquet"
        id = "xxx-yyy"
        store_file_to_disk(extension, id, mock_file)

        path = Path("xxx-yyy-test.parquet")
        mock_store_parquet_file_to_disk.assert_called_once_with(path, False, mock_file)

    @patch("api.common.data_handlers.store_parquet_file_to_disk")
    def test_store_file_to_disk_parquet_chunked(self, mock_store_parquet_file_to_disk):
        mock_file = UploadFile(filename="test.parquet", file=None)
        extension = "parquet"
        id = "xxx-yyy"
        to_chunk = True
        store_file_to_disk(extension, id, mock_file, to_chunk)

        path = Path("xxx-yyy-test.parquet")
        mock_store_parquet_file_to_disk.assert_called_once_with(path, True, mock_file)


class TestStoreCSVFileToDisk:
    def test_store_csv_file_to_disk(self):
        file_data = open("./test/api/resources/test_csv.csv", "rb")
        mock_file = UploadFile(filename="test.csv", file=file_data)
        temp_out_path = tempfile.mkstemp()[1]
        path = Path(temp_out_path)
        store_csv_file_to_disk(path, False, mock_file)

        df1 = pd.read_csv("./test/api/resources/test_csv.csv")
        df2 = pd.read_csv(temp_out_path)

        assert_frame_equal(df1, df2)
        os.remove(temp_out_path)


class TestStoreParquetFileToDisk:
    def test_store_parquet_file_to_disk(self):
        file_data = open("./test/api/resources/test_parquet.parquet", "rb")
        mock_file = UploadFile(filename="test.parquet", file=file_data)
        temp_out_path = tempfile.mkstemp()[1]
        path = Path(temp_out_path)
        store_csv_file_to_disk(path, False, mock_file)

        df1 = pd.read_parquet(
            "./test/api/resources/test_parquet.parquet", engine="pyarrow"
        )
        df2 = pd.read_parquet(temp_out_path, engine="pyarrow")

        assert_frame_equal(df1, df2)
        os.remove(temp_out_path)


class TestConstructChunkedDataframe:
    @patch("api.common.data_handlers.pd")
    def test_construct_chunked_dataframe_csv(self, mock_pd):
        path = Path("file/path.csv")

        construct_chunked_dataframe(path)
        mock_pd.read_csv.assert_called_once_with(
            path, encoding=CONTENT_ENCODING, sep=",", chunksize=CHUNK_SIZE
        )

    @patch("api.common.data_handlers.pq")
    def test__construct_chunked_dataframe_parquet(self, mock_pq):
        path = Path("file/path.parquet")
        mock_parquet_file = Mock()
        mock_pq.ParquetFile.return_value = mock_parquet_file

        construct_chunked_dataframe(path)
        mock_pq.ParquetFile.assert_called_once_with("file/path.parquet")
        mock_parquet_file.iter_batches.assert_called_once_with(batch_size=CHUNK_SIZE)
