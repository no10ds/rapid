from typing import List
from unittest.mock import patch

import pytest

from api.application.services.authorisation.acceptable_permissions import (
    AcceptablePermissions,
    generate_acceptable_scopes,
)
from api.application.services.protected_domain_service import ProtectedDomainService
from api.common.config.auth import SensitivityLevel


class TestAcceptablePermissions:
    @pytest.mark.parametrize(
        "accepted_scopes, token_scopes",
        [
            # READ endpoint
            (
                AcceptablePermissions(
                    required=set(), optional={"READ_ALL", "READ_PUBLIC"}
                ),
                ["READ_PUBLIC"],
            ),
            # WRITE endpoint
            (
                AcceptablePermissions(required=set(), optional={"WRITE_PUBLIC"}),
                ["WRITE_PUBLIC"],
            ),
            # Standalone action endpoints
            (
                AcceptablePermissions(required={"USER_ADMIN"}, optional=set()),
                ["USER_ADMIN"],
            ),
            (
                AcceptablePermissions(required={"DATA_ADMIN"}, optional=set()),
                ["DATA_ADMIN"],
            ),
        ],
    )
    def test_scopes_satisfy_acceptable_scopes(
        self, accepted_scopes: AcceptablePermissions, token_scopes: List[str]
    ):
        assert accepted_scopes.satisfied_by(token_scopes) is True

    @pytest.mark.parametrize(
        "accepted_scopes, token_scopes",
        [
            # READ endpoint
            (
                AcceptablePermissions(
                    required=set(), optional={"READ_ALL", "READ_PUBLIC"}
                ),
                [],
            ),  # No token scopes
            # WRITE endpoint
            (
                AcceptablePermissions(required=set(), optional={"WRITE_PUBLIC"}),
                ["READ_PUBLIC", "READ_ALL"],
            ),
            # Standalone action endpoints
            (
                AcceptablePermissions(required={"USER_ADMIN"}, optional=set()),
                ["READ_ALL"],
            ),
            (
                AcceptablePermissions(required={"DATA_ADMIN"}, optional=set()),
                ["WRITE_ALL"],
            ),
        ],
    )
    def test_scopes_do_not_satisfy_acceptable_scopes(
        self, accepted_scopes: AcceptablePermissions, token_scopes: List[str]
    ):
        assert accepted_scopes.satisfied_by(token_scopes) is False


class TestAcceptablePermissionsGeneration:
    @patch.object(ProtectedDomainService, "list_protected_domains")
    @pytest.mark.parametrize(
        "domain, sensitivity, endpoint_scopes, acceptable_scopes",
        [
            (
                "domain",
                SensitivityLevel.PUBLIC,
                ["READ"],
                AcceptablePermissions(  # noqa: E126
                    required=set(),
                    optional={
                        "READ_ALL",
                        "READ_PUBLIC",
                        "READ_PRIVATE",
                    },
                ),
            ),
            (
                "domain",
                SensitivityLevel.PUBLIC,
                ["USER_ADMIN", "READ"],
                AcceptablePermissions(  # noqa: E126
                    required={"USER_ADMIN"},
                    optional={
                        "READ_ALL",
                        "READ_PUBLIC",
                        "READ_PRIVATE",
                    },
                ),
            ),
            (
                "domain",
                SensitivityLevel.PRIVATE,
                ["USER_ADMIN", "READ", "WRITE"],  # noqa: E126
                AcceptablePermissions(  # noqa: E126
                    required={"USER_ADMIN"},
                    optional={
                        "READ_ALL",
                        "WRITE_ALL",
                        "READ_PRIVATE",
                        "WRITE_PRIVATE",
                    },
                ),
            ),
            (
                None,
                None,
                ["USER_ADMIN"],
                AcceptablePermissions(
                    required={"USER_ADMIN"}, optional=set()
                ),  # noqa: E126
            ),
            (
                "domain",
                SensitivityLevel.PROTECTED,
                ["WRITE"],
                AcceptablePermissions(
                    required=set(), optional={"WRITE_ALL", "WRITE_PROTECTED_DOMAIN"}
                ),  # noqa: E126
            ),
            (
                None,
                SensitivityLevel.PUBLIC,
                ["READ"],
                AcceptablePermissions(  # noqa: E126
                    required=set(),
                    optional={
                        "READ_ALL",
                        "READ_PROTECTED_TEST",
                        "READ_PRIVATE",
                        "READ_PUBLIC",
                    },
                ),
            ),
            (
                None,
                SensitivityLevel.PUBLIC,
                ["READ", "WRITE"],
                AcceptablePermissions(  # noqa: E126
                    required=set(),
                    optional={
                        "READ_ALL",
                        "READ_PROTECTED_TEST",
                        "READ_PRIVATE",
                        "READ_PUBLIC",
                        "WRITE_ALL",
                        "WRITE_PROTECTED_TEST",
                        "WRITE_PRIVATE",
                        "WRITE_PUBLIC",
                    },
                ),
            ),
        ],
    )
    def test_generate_acceptable_permissions(
        self,
        mock_list_protected_domains,
        domain: str,
        sensitivity: SensitivityLevel,
        endpoint_scopes: List[str],
        acceptable_scopes: AcceptablePermissions,
    ):
        mock_list_protected_domains.return_value = ["test"]
        result = generate_acceptable_scopes(endpoint_scopes, sensitivity, domain)
        assert result == acceptable_scopes
