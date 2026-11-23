from unittest.mock import Mock

import pytest

from clap_ops_service.create_admin import create_admin_account


def test_create_admin_account_requires_name(db_session: Mock) -> None:
    with pytest.raises(ValueError, match="Name is required"):
        create_admin_account(
            db_session,
            name=" ",
            email="admin@example.com",
            password="a-secure-password",
            is_superadmin=True,
            fleet_ids=[],
        )

    db_session.add.assert_not_called()


def test_create_admin_account_rejects_name_over_100_characters(
    db_session: Mock,
) -> None:
    with pytest.raises(ValueError, match="at most 100 characters"):
        create_admin_account(
            db_session,
            name="A" * 101,
            email="admin@example.com",
            password="a-secure-password",
            is_superadmin=True,
            fleet_ids=[],
        )
