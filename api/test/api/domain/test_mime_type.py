import pytest

from api.common.custom_exceptions import UserError
from api.domain.mime_type import MimeType


class TestSchema:
    @pytest.mark.parametrize("output_format", ["*/*", None, "", "application/json"])
    def test_sets_application_json(self, output_format: str):
        actual_output_type = MimeType.to_mimetype(output_format)
        assert actual_output_type == MimeType.APPLICATION_JSON

    def test_sets_text_csv(self):
        actual_output_type = MimeType.to_mimetype("text/csv")
        assert actual_output_type == MimeType.TEXT_CSV

    @pytest.mark.parametrize(
        "output_format", ["application/xml", "text/plain", "text/css"]
    )
    def test_throws_error_for_invalid_types(self, output_format: str):
        with pytest.raises(UserError):
            MimeType.to_mimetype(output_format)
