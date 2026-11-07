from uuid import UUID

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.vehicle import VehicleCreate, VehicleUpdate
from clap_ops_service.database.models import Vehicle


class VehicleService:
    def __init__(self, db: Session):
        self.db = db

    def create_vehicle(self, vehicle_data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**vehicle_data.model_dump(exclude={"created_at"}))
        self.db.add(vehicle)
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            if isinstance(error.orig, UniqueViolation):
                raise ValueError("A vehicle with this internal_id already exists") from error
            raise RuntimeError("Unexpected database integrity error while creating vehicle") from error
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError("Unexpected error occurred while creating vehicle") from error
        self.db.refresh(vehicle)
        return vehicle

    def get_vehicle(self, vehicle_id: UUID) -> Vehicle:
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise ValueError("Vehicle not found")
        return vehicle

    def list_vehicles(self) -> list[Vehicle]:
        return self.db.query(Vehicle).order_by(Vehicle.internal_id).all()

    def update_vehicle(self, vehicle_id: UUID, vehicle_data: VehicleUpdate) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)
        for field, value in vehicle_data.model_dump(exclude_unset=True).items():
            setattr(vehicle, field, value)
        try:
            self.db.commit()
            self.db.refresh(vehicle)
        except IntegrityError as error:
            self.db.rollback()
            if isinstance(error.orig, UniqueViolation):
                raise ValueError("A vehicle with this internal_id already exists") from error
            raise RuntimeError("Unexpected database integrity error while updating vehicle") from error
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError("Unexpected error occurred while updating vehicle") from error
        return vehicle

    def delete_vehicle(self, vehicle_id: UUID) -> None:
        vehicle = self.get_vehicle(vehicle_id)
        self.db.delete(vehicle)
        try:
            self.db.commit()
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError("Unexpected error occurred while deleting vehicle") from error
