from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.fuel_history import (
    FuelHistoryCreate,
    FuelHistoryUpdate,
)
from clap_ops_service.database.models import FuelHistory, Vehicle
from clap_ops_service.services.database_helpers import database_operation
from clap_ops_service.services.exceptions import ConflictError, NotFoundError


class FuelHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def _get_vehicle(self, fleet_id: UUID, vehicle_id: UUID) -> Vehicle:
        vehicle = (
            self.db.query(Vehicle)
            .filter(Vehicle.fleet_id == fleet_id, Vehicle.id == vehicle_id)
            .first()
        )
        if vehicle is None:
            raise NotFoundError("Vehicle not found")
        return vehicle

    def _previous_entry(
        self,
        vehicle_id: UUID,
        entry_date,
    ) -> FuelHistory | None:
        return (
            self.db.query(FuelHistory)
            .filter(
                FuelHistory.vehicle_id == vehicle_id,
                FuelHistory.date <= entry_date,
            )
            .order_by(FuelHistory.date.desc(), FuelHistory.created_at.desc())
            .first()
        )

    @staticmethod
    def _fuel_price(total_price: Decimal, volume: Decimal) -> Decimal:
        return (total_price / volume).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )

    def add_fuel_entry(
        self,
        fleet_id: UUID,
        entry_data: FuelHistoryCreate,
    ) -> FuelHistory:
        vehicle = self._get_vehicle(fleet_id, entry_data.vehicle_id)
        if entry_data.odometer < vehicle.current_odometer:
            raise ConflictError(
                "Odometer reading cannot be lower than the vehicle's current odometer"
            )

        previous = self._previous_entry(
            entry_data.vehicle_id,
            entry_data.date,
        )
        entry = FuelHistory(
            **entry_data.model_dump(),
            fuel_price=self._fuel_price(
                entry_data.total_price,
                entry_data.volume,
            ),
            previous_entry_id=previous.id if previous is not None else None,
            previous_entry_date=previous.date if previous is not None else None,
        )
        self.db.add(entry)
        if entry_data.odometer > vehicle.current_odometer:
            vehicle.current_odometer = entry_data.odometer

        with database_operation(self.db, "add fuel entry"):
            self.db.commit()
            self.db.refresh(entry)
        return entry

    def get_fuel_entry(
        self,
        fleet_id: UUID,
        entry_id: UUID,
    ) -> FuelHistory:
        entry = (
            self.db.query(FuelHistory)
            .join(Vehicle, Vehicle.id == FuelHistory.vehicle_id)
            .filter(
                Vehicle.fleet_id == fleet_id,
                FuelHistory.id == entry_id,
            )
            .first()
        )
        if entry is None:
            raise NotFoundError("Fuel history entry not found")
        return entry

    def list_fuel_history(self, fleet_id: UUID) -> list[FuelHistory]:
        return (
            self.db.query(FuelHistory)
            .join(Vehicle, Vehicle.id == FuelHistory.vehicle_id)
            .filter(Vehicle.fleet_id == fleet_id)
            .order_by(FuelHistory.date.desc(), FuelHistory.created_at.desc())
            .all()
        )

    def update_fuel_entry(
        self,
        fleet_id: UUID,
        entry_id: UUID,
        entry_data: FuelHistoryUpdate,
    ) -> FuelHistory:
        entry = self.get_fuel_entry(fleet_id, entry_id)
        values = entry_data.model_dump(exclude_unset=True)

        vehicle_id = values.get("vehicle_id", entry.vehicle_id)
        vehicle = self._get_vehicle(fleet_id, vehicle_id)
        odometer = values.get("odometer", entry.odometer)
        if odometer < vehicle.current_odometer:
            raise ConflictError(
                "Odometer reading cannot be lower than the vehicle's current odometer"
            )

        for field, value in values.items():
            setattr(entry, field, value)

        entry_date = values.get("date", entry.date)
        volume = values.get("volume", entry.volume)
        total_price = values.get("total_price", entry.total_price)
        entry.fuel_price = self._fuel_price(total_price, volume)

        previous = self._previous_entry(vehicle_id, entry_date)
        if previous is not None and previous.id == entry.id:
            previous = (
                self.db.query(FuelHistory)
                .filter(
                    FuelHistory.vehicle_id == vehicle_id,
                    FuelHistory.date <= entry_date,
                    FuelHistory.id != entry.id,
                )
                .order_by(FuelHistory.date.desc(), FuelHistory.created_at.desc())
                .first()
            )
        entry.previous_entry_id = previous.id if previous is not None else None
        entry.previous_entry_date = previous.date if previous is not None else None

        if odometer > vehicle.current_odometer:
            vehicle.current_odometer = odometer

        with database_operation(self.db, "update fuel entry"):
            self.db.commit()
            self.db.refresh(entry)
        return entry

    def delete_fuel_entry(self, fleet_id: UUID, entry_id: UUID) -> None:
        entry = self.get_fuel_entry(fleet_id, entry_id)
        self.db.delete(entry)
        with database_operation(self.db, "delete fuel entry"):
            self.db.commit()
