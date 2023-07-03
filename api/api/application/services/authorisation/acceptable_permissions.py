from dataclasses import dataclass
from typing import Set, List

from api.application.services.protected_domain_service import ProtectedDomainService
from api.common.config.auth import Action, SensitivityLevel


@dataclass
class AcceptablePermissions:
    required: Set[str]
    optional: Set[str]

    def satisfied_by(self, token_scopes: List[str]) -> bool:
        all_required = all(
            [required_scope in token_scopes for required_scope in self.required]
        )
        any_optional = (
            any([any_scope in token_scopes for any_scope in self.optional])
            if self.optional
            else True
        )

        return all_required and any_optional


def generate_acceptable_scopes(
    endpoint_actions: List[str], sensitivity: SensitivityLevel, domain: str = None
) -> AcceptablePermissions:
    protected_domain_service = ProtectedDomainService()
    endpoint_actions = [Action.from_string(action) for action in endpoint_actions]

    required_scopes = set()
    optional_scopes = set()

    for action in endpoint_actions:

        if action in Action.standalone_actions():
            required_scopes.add(action.value)
            continue

        acceptable_sensitivities = _get_acceptable_sensitivity_values(
            domain, sensitivity
        )

        optional_scopes.add(f"{action.value}_ALL")
        for acceptable_sensitivity in acceptable_sensitivities:
            optional_scopes.add(f"{action.value}_{acceptable_sensitivity}")

        if not domain and sensitivity == SensitivityLevel.PUBLIC:
            optional_scopes.update(
                [
                    f"{action.value}_{SensitivityLevel.PROTECTED.value}_{item.upper()}"
                    for item in protected_domain_service.list_protected_domains()
                ]
            )

    return AcceptablePermissions(required_scopes, optional_scopes)


def _get_acceptable_sensitivity_values(
    domain: str, sensitivity: SensitivityLevel
) -> List[str]:
    if sensitivity == SensitivityLevel.PROTECTED:
        return [f"{SensitivityLevel.PROTECTED.value}_{domain.upper()}"]
    else:
        implied_sensitivity_map = {
            # The levels in the values imply the levels in the key
            SensitivityLevel.PUBLIC: [
                SensitivityLevel.PRIVATE,
                SensitivityLevel.PUBLIC,
            ],
            SensitivityLevel.PRIVATE: [
                SensitivityLevel.PRIVATE,
            ],
        }
        acceptable_sensitivities = (
            implied_sensitivity_map.get(sensitivity, [sensitivity])
            if sensitivity
            else []
        )
        return [sensitivity.value for sensitivity in acceptable_sensitivities]
