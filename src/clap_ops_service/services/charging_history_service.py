from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.charging_history import (
    ChargingHistoryCreate,
    ChargingHistoryUpdate,
)
from clap_ops_service.database.models import ChargingHistory, Vehicle
from clap_ops_service.services.database_helpers import database_operation
from clap_ops_service.services.exceptions import ConflictError, NotFoundError


class ChargingHistoryService:
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
        if vehicle.propulsion_type not in ("ELECTRIC", "HYBRID"):
            raise ConflictError("Charging entries require an electric or hybrid vehicle")
        return vehicle

    def _rebuild_previous_entries(self, vehicle_id: UUID) -> None:
        entries = (
            self.db.query(ChargingHistory)
            .filter(ChargingHistory.vehicle_id == vehicle_id)
            .order_by(
                ChargingHistory.charging_started_at.asc(),
                ChargingHistory.created_at.asc(),
            )
            .all()
        )
        previous = None
        for entry in entries:
            entry.previous_entry_id = previous.id if previous is not None else None
            entry.previous_entry_date = (
                previous.charging_started_at if previous is not None else None
            )
            previous = entry

    @staticmethod
    def _duration_minutes(started_at, ended_at) -> int:
        seconds = int((ended_at - started_at).total_seconds())
        return max(0, seconds // 60)

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def add_charging_entry(
        self,
        fleet_id: UUID,
        entry_data: ChargingHistoryCreate,
        created_by_name: str,
        created_by_admin_id: UUID,
    ) -> ChargingHistory:
        vehicle = self._get_vehicle(fleet_id, entry_data.vehicle_id)
        if entry_data.charging_ended_at < entry_data.charging_started_at:
            raise ConflictError("Charging end must be at or after charging start")

        duration = self._duration_minutes(
            entry_data.charging_started_at,
            entry_data.charging_ended_at,
        )
        energy_cost = self._money(
            entry_data.total_energy_kwh * entry_data.energy_price
        )
        total_cost = energy_cost
        entry = ChargingHistory(
            vehicle_id=entry_data.vehicle_id,
            created_by_name=created_by_name,
            created_by_admin_id=created_by_admin_id,
            vendor=entry_data.vendor,
            charging_started_at=entry_data.charging_started_at,
            charging_ended_at=entry_data.charging_ended_at,
            charging_duration_minutes=duration,
            odometer=entry_data.odometer,
            total_energy_kwh=entry_data.total_energy_kwh,
            energy_price=entry_data.energy_price,
            energy_cost=energy_cost,
            total_cost=total_cost,
        )
        self.db.add(entry)
        if entry_data.odometer > vehicle.current_odometer:
            vehicle.current_odometer = entry_data.odometer

        with database_operation(self.db, "add charging entry"):
            self.db.flush()
            self._rebuild_previous_entries(entry_data.vehicle_id)
            self.db.commit()
            self.db.refresh(entry)
        return entry

    def get_charging_entry(
        self,
        fleet_id: UUID,
        entry_id: UUID,
    ) -> ChargingHistory:
        entry = (
            self.db.query(ChargingHistory)
            .join(Vehicle, Vehicle.id == ChargingHistory.vehicle_id)
            .filter(
                Vehicle.fleet_id == fleet_id,
                ChargingHistory.id == entry_id,
            )
            .first()
        )
        if entry is None:
            raise NotFoundError("Charging history entry not found")
        return entry

    def list_charging_history(self, fleet_id: UUID) -> list[ChargingHistory]:
        return (
            self.db.query(ChargingHistory)
            .join(Vehicle, Vehicle.id == ChargingHistory.vehicle_id)
            .filter(Vehicle.fleet_id == fleet_id)
            .order_by(
                ChargingHistory.charging_started_at.desc(),
                ChargingHistory.created_at.desc(),
            )
            .all()
        )

    def update_charging_entry(
        self,
        fleet_id: UUID,
        entry_id: UUID,
        entry_data: ChargingHistoryUpdate,
    ) -> ChargingHistory:
        entry = self.get_charging_entry(fleet_id, entry_id)
        original_vehicle_id = entry.vehicle_id
        values = entry_data.model_dump(exclude_unset=True)

        vehicle_id = values.get("vehicle_id", entry.vehicle_id)
        vehicle = self._get_vehicle(fleet_id, vehicle_id)
        odometer = values.get("odometer", entry.odometer)

        for field, value in values.items():
            setattr(entry, field, value)

        started_at = values.get("charging_started_at", entry.charging_started_at)
        ended_at = values.get("charging_ended_at", entry.charging_ended_at)
        if ended_at < started_at:
            raise ConflictError("Charging end must be at or after charging start")

        total_energy = values.get("total_energy_kwh", entry.total_energy_kwh)
        energy_price = values.get("energy_price", entry.energy_price)
        entry.charging_duration_minutes = self._duration_minutes(
            started_at,
            ended_at,
        )
        entry.energy_cost = self._money(total_energy * energy_price)
        entry.total_cost = entry.energy_cost

        if odometer > vehicle.current_odometer:
            vehicle.current_odometer = odometer

        with database_operation(self.db, "update charging entry"):
            self.db.flush()
            self._rebuild_previous_entries(original_vehicle_id)
            if vehicle_id != original_vehicle_id:
                self._rebuild_previous_entries(vehicle_id)
            self.db.commit()
            self.db.refresh(entry)
        return entry

    def delete_charging_entry(self, fleet_id: UUID, entry_id: UUID) -> None:
        entry = self.get_charging_entry(fleet_id, entry_id)
        vehicle_id = entry.vehicle_id
        self.db.delete(entry)
        with database_operation(self.db, "delete charging entry"):
            self.db.flush()
            self._rebuild_previous_entries(vehicle_id)
            self.db.commit()
