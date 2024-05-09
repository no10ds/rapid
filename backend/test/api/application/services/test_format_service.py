import csv
import pandas as pd

from api.application.services.format_service import FormatService
from api.domain.mime_type import MimeType


class TestFormatService:
    def setup_method(self):
        self.df = pd.DataFrame(
            {
                "column1": [1, 2],
                "column2": ["item1", "item2"],
                "area": ["area_1", "area_2"],
            }
        )

    def test_format_to_csv(self):
        output = FormatService.from_df_to_mimetype(self.df, MimeType.TEXT_CSV)
        assert output == self.df.to_csv(quoting=csv.QUOTE_NONNUMERIC, index=False)

    def test_format_to_json(self):
        output = FormatService.from_df_to_mimetype(self.df, MimeType.APPLICATION_JSON)
        assert output == {
            0: {"area": "area_1", "column1": 1, "column2": "item1"},
            1: {"area": "area_2", "column1": 2, "column2": "item2"},
        }
