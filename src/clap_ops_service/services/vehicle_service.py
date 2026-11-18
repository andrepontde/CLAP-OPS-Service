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

    def create_vehicle(self, vehicle_data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**vehicle_data.model_dump(exclude={"created_at"}))
        self.db.add(vehicle)
        with database_operation(
            self.db,
            "create vehicle",
            "A vehicle with this name or VIN already exists",
        ):
            self.db.commit()
            self.db.refresh(vehicle)
        return vehicle

    def get_vehicle(self, vehicle_id: UUID) -> Vehicle:
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise NotFoundError("Vehicle not found")
        return vehicle

    def list_vehicles(self) -> list[Vehicle]:
        return self.db.query(Vehicle).order_by(Vehicle.name).all()

    def update_vehicle(self, vehicle_id: UUID, vehicle_data: VehicleUpdate) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)
        for field, value in vehicle_data.model_dump(exclude_unset=True).items():
            setattr(vehicle, field, value)
        with database_operation(
            self.db,
            "update vehicle",
            "A vehicle with this name or VIN already exists",
        ):
            self.db.commit()
            self.db.refresh(vehicle)
        return vehicle

    def delete_vehicle(self, vehicle_id: UUID) -> None:
        vehicle = self.get_vehicle(vehicle_id)
        self.db.delete(vehicle)
        with database_operation(self.db, "delete vehicle"):
            self.db.commit()
