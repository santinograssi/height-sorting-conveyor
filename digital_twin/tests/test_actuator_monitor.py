"""Tests for the PLC command monitor."""

import unittest

from actuator_monitor import ActuatorMonitor
from config import (
    COIL_ALARM_ACTIVE,
    COIL_CONVEYOR_RUN,
    COIL_DIVERTER_GATE,
)


class FakeDataStore:
    def __init__(self) -> None:
        self.coils = {
            COIL_CONVEYOR_RUN: True,
            COIL_DIVERTER_GATE: False,
            COIL_ALARM_ACTIVE: True,
        }

    def read_coil(self, address: int) -> bool:
        return self.coils[address]


class ActuatorMonitorTests(unittest.TestCase):
    def test_all_three_plc_commands_are_read(self) -> None:
        monitor = ActuatorMonitor(FakeDataStore())

        self.assertEqual(
            monitor.read_commands(),
            {
                "conveyorRun": True,
                "diverterGate": False,
                "alarmActive": True,
            },
        )


if __name__ == "__main__":
    unittest.main()

