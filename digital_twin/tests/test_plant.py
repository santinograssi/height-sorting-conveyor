"""Behavior tests for the conveyor plant simulation."""

import unittest
from unittest.mock import AsyncMock, patch

from config import (
    COIL_CONVEYOR_RUN,
    COIL_OBJECT_DETECTED,
    HEIGHT_BASELINE_MM,
    HEIGHT_SHORT_MM,
    REG_HEIGHT_READING,
)
from plant import PlantSimulator


class FakeDataStore:
    def __init__(self, conveyor_running: bool) -> None:
        self.coils = {COIL_CONVEYOR_RUN: conveyor_running}
        self.registers = {}

    def read_coil(self, address: int) -> bool:
        return self.coils.get(address, False)

    def write_coil(self, address: int, value: bool) -> None:
        self.coils[address] = value

    def write_input_register(self, address: int, value: int) -> None:
        self.registers[address] = value


class PlantSimulatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_completed_object_cycle_clears_sensors(self) -> None:
        datastore = FakeDataStore(conveyor_running=True)
        plant = PlantSimulator(datastore)

        with (
            patch("plant.random.choice", return_value="short"),
            patch("plant.asyncio.sleep", new=AsyncMock()),
        ):
            await plant.run_object_cycle()

        self.assertFalse(datastore.coils[COIL_OBJECT_DETECTED])
        self.assertEqual(
            datastore.registers[REG_HEIGHT_READING],
            HEIGHT_BASELINE_MM,
        )

    async def test_mid_object_stop_freezes_sensor_readings(self) -> None:
        datastore = FakeDataStore(conveyor_running=False)
        plant = PlantSimulator(datastore)

        with patch("plant.random.choice", return_value="short"):
            await plant.run_object_cycle()

        self.assertTrue(datastore.coils[COIL_OBJECT_DETECTED])
        self.assertEqual(
            datastore.registers[REG_HEIGHT_READING],
            HEIGHT_SHORT_MM,
        )


if __name__ == "__main__":
    unittest.main()

