import pytest

from api.common.custom_exceptions import UserError
from api.domain.user import UserRequest


@pytest.fixture
def custom_user_regex_default():
    return "[a-zA-Z][a-zA-Z0-9@._-]{2,127}"


@pytest.fixture
def custom_user_regex_non_default():
    return "^[A-Z][A-Za-z0-9]{3,50}$"


class TestUserRequest:
    @pytest.mark.parametrize(
        "provided_username",
        [
            "username_name",
            "username_name2",
            "username@email.com",
            "VA.li_d@na-mE",
            "A....",
            "S1234",
        ],
    )
    def test_get_validated_username(self, provided_username, custom_user_regex_default):
        request = UserRequest(username=provided_username, email="user@email.com")

        # Overrwrite env variable on fn import
        CUSTOM_USERNAME_REGEX = custom_user_regex_default
        try:
            validated_name = request.get_validated_username()
            assert validated_name == provided_username
        except UserError:
            pytest.fail("An unexpected UserError was thrown")

    @pytest.mark.parametrize(
        "provided_username",
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
    def test_raises_error_when_invalid_username(
        self, provided_username, custom_user_regex_default
    ):
        request = UserRequest(username=provided_username, email="user@email.com")
        # Overrwrite env variable on fn import
        CUSTOM_USERNAME_REGEX = custom_user_regex_default
        with pytest.raises(UserError, match="Invalid username provided"):
            request.get_validated_username()

    @pytest.mark.parametrize(
        "provided_username",
        [
            "Ttest123",
            "TCheck",
            "SamCheck",
            "Sam123Check456",
            "S1234",
        ],
    )
    def test_get_validated_username_custom_regex(
        self, provided_username, custom_user_regex_non_default
    ):
        CUSTOM_USERNAME_REGEX = custom_user_regex_non_default
        request = UserRequest(username=provided_username, email="user@email.com")
        try:
            validated_name = request.get_validated_username()
            assert validated_name == provided_username
        except UserError:
            pytest.fail("An unexpected UserError was thrown")

    @pytest.mark.parametrize(
        "provided_username",
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
    def test_raises_error_when_invalid_username(
        self, provided_username, custom_user_regex_non_default
    ):
        CUSTOM_USERNAME_REGEX = custom_user_regex_non_default

        request = UserRequest(username=provided_username, email="user@email.com")

        with pytest.raises(UserError, match="Invalid username provided"):
            request.get_validated_username()

    @pytest.mark.parametrize(
        "provided_email",
        [
            "username_name@example1.com",
            "username_name2@example1.com",
            "VA.li_dna-mE@example1.com",
            "VA.li_dna-mE@example2.com",
            "S1234@example2.com",
        ],
    )
    def test_get_validated_email(self, provided_email):
        request = UserRequest(username="user_name", email=provided_email)

        try:
            validated_email = request.get_validated_email()
            assert validated_email == provided_email
        except UserError:
            pytest.fail("An unexpected UserError was thrown")

    @pytest.mark.parametrize(
        "provided_email",
        [
            "",
            " ",
            "username_name",
            "username_name2",
            "username_name@example1.com@email.com",
            "username@emailemail.com",
            "VA.li_dna-mE",
            "A....",
            "S1234",
            "SOme$@no-valid-email.com",
            "sOMe!name@email..com",
            "(some)namE@email.com",
            "....@email.com",
            "username@fake.example1.com",
        ],
    )
    def test_raises_error_when_invalid_email(self, provided_email):
        request = UserRequest(username="user_name", email=provided_email)

        with pytest.raises(UserError, match="Invalid email provided"):
            request.get_validated_email()
