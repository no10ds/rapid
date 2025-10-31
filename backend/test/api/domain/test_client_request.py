import pytest

from api.common.custom_exceptions import UserError
from api.domain.client import ClientRequest


class TestClientRequest:
    @pytest.mark.parametrize(
        "provided_client_name",
        [
            "department_name",
            "department_name2",
            "department@email.com",
            "VA.li_d@na-mE",
            "A....",
            "S1234",
        ],
    )
    def test_get_validated_client_name(self, provided_client_name):
        request = ClientRequest(client_name=provided_client_name)

        try:
            validated_name = request.get_validated_client_name()
            assert validated_name == provided_client_name
        except UserError:
            pytest.fail("An unexpected UserError was thrown")

    @pytest.mark.parametrize(
        "provided_client_name",
        [
            "",
            " ",
            "SOme naME",
            "sOMe!name",
            "-some-nAMe",
            "(some)namE",
            "1234",
            "....",
            "A" * 2,
            "A" * 129,
        ],
    )
    def test_raises_error_when_invalid_client_name(self, provided_client_name):
        request = ClientRequest(client_name=provided_client_name)

        with pytest.raises(UserError, match="Invalid client name provided"):
            request.get_validated_client_name()
