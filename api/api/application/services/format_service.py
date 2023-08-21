import csv
from pandas import DataFrame

from api.domain.mime_type import MimeType


class FormatService:
    @staticmethod
    def from_df_to_mimetype(df: DataFrame, mime_type: MimeType):
        if mime_type == MimeType.TEXT_CSV:
            return df.to_csv(quoting=csv.QUOTE_NONNUMERIC, index=False)
        elif mime_type == MimeType.BINARY:
            return df.to_parquet(engine="pyarrow")
        else:
            return df.to_dict(orient="index")
