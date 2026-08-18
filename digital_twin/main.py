"""Application entry point for the Height Sorting Conveyor digital twin."""

import asyncio

from actuator_monitor import ActuatorMonitor
from config import (
    DEVICE_ID,
    SERVER_IP,
    SERVER_PORT,
    SERVER_STARTUP_CHECK_SECONDS,
)
from modbus_server import ModbusDataStore
from plant import PlantSimulator


def print_startup_banner() -> None:
    print("Python Digital Twin -- Height Sorting Conveyor")
    print("(classic pymodbus API, pinned 3.11.4)\n")
    print(f"Modbus TCP server: {SERVER_IP}:{SERVER_PORT}")
    print(f"Device ID: {DEVICE_ID}\n")

async def main() -> None:
    print_startup_banner()

    datastore = ModbusDataStore()
    plant = PlantSimulator(datastore)
    monitor = ActuatorMonitor(datastore)

    server_task = asyncio.create_task(datastore.serve(), name="modbus-server")

    # A healthy server remains pending. If it exits immediately, surface the
    # bind error instead of claiming that the server started successfully.
    await asyncio.sleep(SERVER_STARTUP_CHECK_SECONDS)
    if server_task.done():
        server_task.result()

    print("Modbus server started. Waiting for OpenPLC to command conveyorRun...")

    plant_task = asyncio.create_task(plant.run(), name="plant-simulation")
    monitor_task = asyncio.create_task(monitor.run(), name="actuator-monitor")

    await asyncio.gather(server_task, plant_task, monitor_task)


if __name__ == "__main__":
    asyncio.run(main())

