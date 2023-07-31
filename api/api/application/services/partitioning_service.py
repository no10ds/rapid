from typing import List, Tuple, Hashable, Optional

import pandas as pd
from pydantic import BaseModel

from api.domain.schema import Schema


class Partition(BaseModel):
    keys: Optional[list] = [""]
    path: Optional[str] = ""
    df: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True


def generate_path(group_partitions: List[str], group_info: Tuple[Hashable, ...]) -> str:
    formatted_group_partitions = [
        f"{partition}={value}" for partition, value in zip(group_partitions, group_info)
    ]
    return "/".join(formatted_group_partitions)


def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    return df.drop(labels=columns, axis=1)


def generate_partitioned_data(schema: Schema, df: pd.DataFrame) -> List[Partition]:
    partitions = schema.get_partitions()

    if len(partitions) == 0:
        return non_partitioned_dataframe(df)
    return partitioned_dataframe(df, partitions)


def partitioned_dataframe(df: pd.DataFrame, partitions: List[str]) -> List[Partition]:
    partitioned_data = []
    grouped = df.groupby(by=partitions)
    for group_spec, group_data in grouped:
        group_spec = (group_spec,) if len(partitions) == 1 else group_spec

        cleaned_dataframe = drop_columns(df=group_data, columns=partitions).reset_index(
            drop=True
        )
        partitioned_data.append(
            Partition(
                keys=group_spec,
                path=generate_path(partitions, group_spec),
                df=cleaned_dataframe,
            )
        )
    return partitioned_data


def non_partitioned_dataframe(df: pd.DataFrame) -> List[Partition]:
    return [Partition(df=df)]
