from uuid import UUID

from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.vehicle import VehicleCreate, VehicleUpdate
from clap_ops_service.database.models import Vehicle
from clap_ops_service.services.database_helpers import database_operation
from clap_ops_service.services.exceptions import (
    NotFoundError,
)


class VehicleService:
    def __init__(self, db: Session):
        self.db = db

    def create_vehicle(
        self,
        fleet_id: UUID,
        vehicle_data: VehicleCreate,
    ) -> Vehicle:
        vehicle = Vehicle(
            fleet_id=fleet_id,
            **vehicle_data.model_dump(),
        )
        self.db.add(vehicle)
        with database_operation(
            self.db,
            "create vehicle",
            "A vehicle with this name or VIN already exists",
        ):
            self.db.commit()
            self.db.refresh(vehicle)
        return vehicle

    def get_vehicle(self, fleet_id: UUID, vehicle_id: UUID) -> Vehicle:
        vehicle = (
            self.db.query(Vehicle)
            .filter(
                Vehicle.fleet_id == fleet_id,
                Vehicle.id == vehicle_id,
            )
            .first()
        )
        if vehicle is None:
            raise NotFoundError("Vehicle not found")
        return vehicle

    def list_vehicles(self, fleet_id: UUID) -> list[Vehicle]:
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.fleet_id == fleet_id)
            .order_by(Vehicle.name)
            .all()
        )

    def update_vehicle(
        self,
        fleet_id: UUID,
        vehicle_id: UUID,
        vehicle_data: VehicleUpdate,
    ) -> Vehicle:
        vehicle = self.get_vehicle(fleet_id, vehicle_id)
        values = vehicle_data.model_dump(exclude_unset=True)
        if values.get("propulsion_type") == "ELECTRIC":
            values["fuel_type"] = None
        for field, value in values.items():
            setattr(vehicle, field, value)
        VehicleCreate.model_validate(vehicle)
        with database_operation(
            self.db,
            "update vehicle",
            "A vehicle with this name or VIN already exists",
        ):
            self.db.commit()
            self.db.refresh(vehicle)
        return vehicle

    def delete_vehicle(self, fleet_id: UUID, vehicle_id: UUID) -> None:
        vehicle = self.get_vehicle(fleet_id, vehicle_id)
        self.db.delete(vehicle)
        with database_operation(self.db, "delete vehicle"):
            self.db.commit()
