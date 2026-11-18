from uuid import UUID

from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.fleet import FleetCreate
from clap_ops_service.database.models import (
    Admin,
    Fleet,
    FleetMembership,
)
from clap_ops_service.services.database_helpers import database_operation
from clap_ops_service.services.exceptions import (
    ConflictError,
    NotFoundError,
)


class FleetService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, fleet_data: FleetCreate) -> Fleet:
        fleet = Fleet(**fleet_data.model_dump())
        self.db.add(fleet)
        with database_operation(
            self.db,
            "create fleet",
            "A fleet with this name already exists",
        ):
            self.db.commit()
            self.db.refresh(fleet)
        return fleet

    def list_for_admin(self, admin: Admin) -> list[Fleet]:
        if admin.is_superadmin:
            return self.db.query(Fleet).order_by(Fleet.name).all()
        return (
            self.db.query(Fleet)
            .join(FleetMembership, FleetMembership.fleet_id == Fleet.id)
            .filter(FleetMembership.admin_id == admin.id)
            .order_by(Fleet.name)
            .all()
        )

    def set_membership(
        self,
        fleet_id: UUID,
        admin_id: int,
        role: str,
    ) -> FleetMembership:
        fleet = self.db.query(Fleet).filter(Fleet.id == fleet_id).first()
        if fleet is None:
            raise NotFoundError("Fleet not found")

        admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
        if admin is None:
            raise NotFoundError("Admin not found")

        membership = (
            self.db.query(FleetMembership)
            .filter(
                FleetMembership.fleet_id == fleet_id,
                FleetMembership.admin_id == admin_id,
            )
            .first()
        )
        if membership is None:
            membership = FleetMembership(
                admin_id=admin_id,
                fleet_id=fleet_id,
                role=role,
            )
            self.db.add(membership)
        else:
            membership.role = role

        with database_operation(self.db, "update fleet membership"):
            self.db.commit()
            self.db.refresh(membership)
        return membership
