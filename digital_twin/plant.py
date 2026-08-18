"""Physical-process simulation for objects moving on the conveyor."""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

from config import (
    COIL_CONVEYOR_RUN,
    COIL_OBJECT_DETECTED,
    HEIGHT_BASELINE_MM,
    HEIGHT_SHORT_MM,
    HEIGHT_TALL_MM,
    OBJECT_GAP_STEPS,
    OBJECT_PRESENT_STEPS,
    REG_HEIGHT_READING,
    SIMULATION_STEP_SECONDS,
)

if TYPE_CHECKING:
    from modbus_server import ModbusDataStore


class PlantSimulator:
    """Generate objects and update the simulated field sensors."""

    def __init__(self, datastore: ModbusDataStore) -> None:
        self.datastore = datastore

    def conveyor_is_running(self) -> bool:
        return self.datastore.read_coil(COIL_CONVEYOR_RUN)

    async def run_object_cycle(self) -> None:
        """Present one random object to the height and presence sensors."""
        object_type = random.choice(["short", "tall"])
        height_mm = (HEIGHT_SHORT_MM if object_type == "short" else HEIGHT_TALL_MM)

        print()
        print(
            f"OBJECT ARRIVED  (type={object_type}, "
            f"heightReading={height_mm}mm)"
        )

        self.datastore.write_coil(COIL_OBJECT_DETECTED, True)
        self.datastore.write_input_register(REG_HEIGHT_READING, height_mm)

        # Keep the object under the sensor for about four seconds. If the belt
        # stops, return without clearing either sensor: the physical object is
        # still present, so the readings deliberately remain frozen.
        for _ in range(OBJECT_PRESENT_STEPS):
            if not self.conveyor_is_running():
                print("BELT STOPPED WHILE OBJECT WAS PRESENT -- freezing readings.")
                return
            await asyncio.sleep(SIMULATION_STEP_SECONDS)

        print(f"OBJECT LEFT SENSOR  (heightReading={HEIGHT_BASELINE_MM}mm)")
        self.datastore.write_coil(COIL_OBJECT_DETECTED, False)
        self.datastore.write_input_register(REG_HEIGHT_READING, HEIGHT_BASELINE_MM)

    async def run(self) -> None:
        """Continuously simulate object arrivals while the belt is running."""
        was_running = False

        while True:
            conveyor_running = self.conveyor_is_running()

            if not conveyor_running:
                if was_running:
                    print()
                    print("Belt stopped. Waiting for conveyorRun = TRUE ...")
                was_running = False
                await asyncio.sleep(SIMULATION_STEP_SECONDS)
                continue

            if not was_running:
                print()
                print("Belt running. Starting object-arrival simulation.")
                was_running = True

            # The two-second gap remains interruptible by a Stop command.
            for _ in range(OBJECT_GAP_STEPS):
                if not self.conveyor_is_running():
                    break
                await asyncio.sleep(SIMULATION_STEP_SECONDS)
            else:
                await self.run_object_cycle()
