from api.domain.permission_item import PermissionItem


class TestPermissionItem:
    def test_get_permission_dict(self):
        permission = PermissionItem(
            id="READ_PROTECTED_DOMAIN",
            type="READ",
            sensitivity="PROTECTED",
            domain="DOMAIN",
            layer="LAYER",
        )
        expected_permission_dictionary = {
            "id": "READ_PROTECTED_DOMAIN",
            "type": "READ",
            "sensitivity": "PROTECTED",
            "domain": "DOMAIN",
            "layer": "LAYER",
        }
        assert permission.dict() == expected_permission_dictionary
