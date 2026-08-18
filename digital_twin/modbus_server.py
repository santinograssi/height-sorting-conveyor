"""Modbus TCP datastore and server access.

The plant and monitor use this module instead of depending directly on
``pymodbus``. This keeps all protocol-specific details in one place.
"""

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer

from config import (
    COIL_COUNT,
    DEVICE_ID,
    DISCRETE_INPUT_COUNT,
    HEIGHT_BASELINE_MM,
    HOLDING_REGISTER_COUNT,
    INPUT_REGISTER_COUNT,
    REG_HEIGHT_READING,
    SERVER_IP,
    SERVER_PORT,
)


class ModbusDataStore:
    """Own the Modbus memory used by the digital twin."""

    def __init__(self) -> None:
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [False] * DISCRETE_INPUT_COUNT),
            co=ModbusSequentialDataBlock(0, [False] * COIL_COUNT),
            hr=ModbusSequentialDataBlock(0, [0] * HOLDING_REGISTER_COUNT),
            ir=ModbusSequentialDataBlock(0, [0] * INPUT_REGISTER_COUNT),
        )

        # pymodbus renamed ``slaves`` to ``devices``. Supporting both names
        # makes the compatibility intent explicit while 3.11.4 remains pinned.
        try:
            self.context = ModbusServerContext(devices=store, single=True)
        except TypeError:
            self.context = ModbusServerContext(slaves=store, single=True)

        self.write_input_register(REG_HEIGHT_READING, HEIGHT_BASELINE_MM)

    def read_coil(self, address: int) -> bool:
        """Read one coil from the local server datastore."""
        value = self.context[DEVICE_ID].getValues(1, address, 1)[0]
        return bool(value)

    def write_coil(self, address: int, value: bool) -> None:
        """Write one simulated sensor value to the coil block."""
        self.context[DEVICE_ID].setValues(5, address, [bool(value)])

    def write_input_register(self, address: int, value: int) -> None:
        """Inject a sensor reading into the input-register block.

        Function code 4 selects the input-register memory bank inside the
        pymodbus datastore. This is a local update; no Modbus write request is
        sent over the network because input registers are read-only to clients.
        """
        self.context[DEVICE_ID].setValues(4, address, [int(value)])

    async def serve(self) -> None:
        """Run the Modbus TCP server until the application is stopped."""
        await StartAsyncTcpServer(
            context=self.context,
            address=(SERVER_IP, SERVER_PORT),
        )

