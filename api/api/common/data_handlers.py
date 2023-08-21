import os
import psutil
from typing import Any
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from fastapi import UploadFile, File
from pandas.io.parsers import TextFileReader

from api.common.logger import AppLogger
from api.common.config.constants import (
    CHUNK_SIZE_MB,
    PARQUET_CHUNK_SIZE,
    CONTENT_ENCODING,
)
from api.domain.schema import Schema

CHUNK_SIZE = 200_000


def store_file_to_disk(
    extension: str, id: str, file: UploadFile = File(...), to_chunk: bool = False
) -> Path:
    file_path = Path(f"{id}-{file.filename}")
    AppLogger.info(
        f"Writing incoming file chunk ({CHUNK_SIZE_MB}MB) to disk [{file.filename}]"
    )
    AppLogger.info(f"Available disk space: {psutil.disk_usage('/').free / (2 ** 30)}GB")

    if extension == "csv":
        store_csv_file_to_disk(file_path, to_chunk, file)
    elif extension == "parquet":
        store_parquet_file_to_disk(file_path, to_chunk, file)
    return file_path


def store_csv_file_to_disk(
    file_path: Path, to_chunk: bool, file: UploadFile = File(...)
):
    with open(file_path, "wb") as incoming_file:
        while contents := file.file.read(CHUNK_SIZE_MB):
            incoming_file.write(contents)

            if to_chunk:
                incoming_file.close()
                break


def store_parquet_file_to_disk(
    file_path: Path, to_chunk: bool, file: UploadFile = File(...)
):
    parquet_file = pq.ParquetFile(file.file)
    for index, batch in enumerate(parquet_file.iter_batches(PARQUET_CHUNK_SIZE)):
        if index == 0:
            writer = pq.ParquetWriter(file_path.as_posix(), batch.schema)

        table = pa.Table.from_batches([batch])
        writer.write_table(table)

        if to_chunk:
            break
    writer.close()


def construct_chunked_dataframe(
    file_path: Path,
) -> TextFileReader | Any | None:
    # Loads the file from the local path and splits into each dataframe chunk for processing
    # when loading csv Pandas returns an IO iterable TextFileReader but for a Pyarrow chunking
    # it retuns an iterable of pyarrow.RecordBatch, we then pass this through the extra function
    # to return a dataframe compatiable format
    extension = file_path.as_posix().split(".")[-1].lower()
    if extension == "csv":
        chunk = pd.read_csv(
            file_path, encoding=CONTENT_ENCODING, sep=",", chunksize=CHUNK_SIZE
        )
        return chunk
        # return get_dataframe_from_chunk_type(chunk)
    elif extension == "parquet":
        parquet_file = pq.ParquetFile(file_path.as_posix())
        chunk = parquet_file.iter_batches(batch_size=CHUNK_SIZE)
        # return get_dataframe_from_chunk_type(chunk)
        return chunk


def get_dataframe_from_chunk_type(
    chunk: TextFileReader | Any,
) -> pd.DataFrame:
    # Work out the processing that may need to occur on a chunk to get it into a Pandas compatible format
    # for csv this is TextFileReader for Pyarrow Parquet we need to perform a to_pandas()
    if isinstance(chunk, pd.DataFrame):
        return chunk
    elif isinstance(chunk, pa.RecordBatch):
        return chunk.to_pandas()


def delete_incoming_raw_file(
    schema: Schema, file_path: Path, raw_file_identifier: str = None
):
    raw_file_identifier_string = f"Raw file identifier: {raw_file_identifier}"
    try:
        os.remove(file_path.name)
        AppLogger.info(
            f"""Temporary upload file for {schema.metadata.string_representation()} deleted. {raw_file_identifier_string if raw_file_identifier is not None else ''}"""
        )
    except (FileNotFoundError, TypeError) as error:
        AppLogger.error(
            f"Temporary upload file for {schema.metadata.string_representation()} not deleted. {raw_file_identifier_string if raw_file_identifier is not None else ''}. Detail: {error}"
        )
