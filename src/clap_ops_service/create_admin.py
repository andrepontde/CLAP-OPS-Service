from getpass import getpass
from uuid import UUID

from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from clap_ops_service.database.connection import SessionLocal
from clap_ops_service.database.models import (
    Admin,
    Fleet,
    FleetMembership,
)

PASSWORD_HASHER = PasswordHash.recommended()
MINIMUM_PASSWORD_LENGTH = 12


def create_admin_account(
    db: Session,
    email: str,
    password: str,
    is_superadmin: bool,
    fleet_ids: list[UUID],
) -> Admin:
    normalized_email = email.strip().casefold()
    if not normalized_email:
        raise ValueError("Email is required")
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MINIMUM_PASSWORD_LENGTH} characters")

    admin = Admin(
        email=normalized_email,
        password_hash=PASSWORD_HASHER.hash(password),
        is_superadmin=is_superadmin,
    )
    db.add(admin)
    try:
        db.flush()
        unique_fleet_ids = list(dict.fromkeys(fleet_ids))
        for fleet_id in unique_fleet_ids:
            db.add(
                FleetMembership(
                    admin_id=admin.id,
                    fleet_id=fleet_id,
                    role="MANAGER",
                )
            )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("An account with that email already exists") from error
    db.refresh(admin)
    return admin


def main() -> None:
    try:
        with SessionLocal() as db:
            has_admin = db.query(Admin).first() is not None
            fleet_ids: list[UUID] = []

            if not has_admin:
                is_superadmin = True
                fleet_name = input("Fleet name: ").strip()
                if not fleet_name:
                    raise SystemExit("Fleet name is required")
                fleet = Fleet(name=fleet_name)
                db.add(fleet)
                db.flush()
                fleet_ids = [fleet.id]
            else:
                answer = input("Create as superadmin? [y/N]: ").strip().lower()
                is_superadmin = answer in {"y", "yes"}
                if not is_superadmin:
                    fleets = db.query(Fleet).order_by(Fleet.name).all()
                    if not fleets:
                        raise SystemExit(
                            "Create a fleet before creating a restricted admin"
                        )
                    print("Available fleets:")
                    for index, fleet in enumerate(fleets, start=1):
                        print(f"{index}. {fleet.name}")
                    selections = input(
                        "Fleet numbers separated by commas: "
                    ).strip()
                    for selection in selections.split(","):
                        if not selection.strip().isdigit():
                            raise SystemExit("Fleet selections must be numbers")
                        index = int(selection.strip())
                        if not 1 <= index <= len(fleets):
                            raise SystemExit("Invalid fleet selection")
                        fleet_ids.append(fleets[index - 1].id)

            email = input("Admin email: ").strip()
            password = getpass("Password: ")
            confirmation = getpass("Confirm password: ")
            if password != confirmation:
                raise SystemExit("Passwords do not match")

            admin = create_admin_account(
                db,
                email,
                password,
                is_superadmin,
                fleet_ids,
            )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(f"Created admin account for {admin.email}")
