"""Console monitoring for actuator and alarm commands from OpenPLC."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from config import (
    COIL_ALARM_ACTIVE,
    COIL_CONVEYOR_RUN,
    COIL_DIVERTER_GATE,
    MONITOR_INTERVAL_SECONDS,
)

if TYPE_CHECKING:
    from modbus_server import ModbusDataStore


class ActuatorMonitor:
    """Print PLC command changes without mixing them into plant behavior."""

    def __init__(self, datastore: ModbusDataStore) -> None:
        self.datastore = datastore

    def read_commands(self) -> dict[str, bool]:
        return {
            "conveyorRun": self.datastore.read_coil(COIL_CONVEYOR_RUN),
            "diverterGate": self.datastore.read_coil(COIL_DIVERTER_GATE),
            "alarmActive": self.datastore.read_coil(COIL_ALARM_ACTIVE),
        }

    async def run(self) -> None:
        previous: dict[str, bool | None] = {
            "conveyorRun": None,
            "diverterGate": None,
            "alarmActive": None,
        }

        while True:
            current = self.read_commands()

            for name, value in current.items():
                if value != previous[name]:
                    print(f"PLC COMMAND: {name} = {value}")

            previous = current
            await asyncio.sleep(MONITOR_INTERVAL_SECONDS)
