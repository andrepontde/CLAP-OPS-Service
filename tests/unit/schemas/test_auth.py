from uuid import uuid4

import pytest
from pydantic import ValidationError

from clap_ops_service.api.v1.schemas.auth import CurrentAdminResponse


def test_current_admin_response_includes_fleet_memberships() -> None:
    fleet_id = uuid4()
    response = CurrentAdminResponse(
        id=1,
        email="admin@example.com",
        is_superadmin=False,
        fleets=[
            {
                "id": fleet_id,
                "name": "North Fleet",
                "role": "MANAGER",
            }
        ],
    )

    assert response.fleets[0].id == fleet_id
    assert response.fleets[0].role == "MANAGER"


def test_current_admin_response_rejects_unknown_fleet_role() -> None:
    with pytest.raises(ValidationError):
        CurrentAdminResponse(
            id=1,
            email="admin@example.com",
            is_superadmin=False,
            fleets=[
                {
                    "id": uuid4(),
                    "name": "North Fleet",
                    "role": "ADMIN",
                }
            ],
        )
