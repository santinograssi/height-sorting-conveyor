# Python Digital Twin

This application simulates the physical conveyor, products, presence sensor, and height sensor. It exposes simulated field I/O through a Modbus TCP server so OpenPLC can control the process.

The code pins the verified dependency `pymodbus==3.11.4` to keep the communication behavior reproducible.

## Architecture

```text
main.py
├── ModbusDataStore      Modbus memory and TCP server
├── PlantSimulator       Products, conveyor, and sensors
└── ActuatorMonitor      PLC output and alarm changes
```

| File | Responsibility |
|---|---|
| `config.py` | Network settings, Modbus addresses, sensor values, and timings |
| `modbus_server.py` | pymodbus datastore access and asynchronous TCP server |
| `plant.py` | Object arrival, height selection, and sensor behavior |
| `actuator_monitor.py` | Console reporting of PLC command changes |
| `main.py` | Creates and runs all asynchronous tasks |
| `tests/` | Interface and behavior regression tests |

Keeping these concerns separate makes the project easier to understand, test, and extend.

## Network configuration

| Setting | Value |
|---|---:|
| Host | `127.0.0.1` |
| Port | `1502` |
| Device ID | `1` |

## Simulation behavior

- The twin remains idle until OpenPLC sets `conveyorRun = TRUE`.
- While running, there is a two-second gap before every new product.
- Each product is randomly short (`220 mm`) or tall (`100 mm`).
- A product normally remains under the sensors for four seconds.
- When it leaves, `objectDetected` becomes false and `heightReading` returns to the empty-belt baseline of `300 mm`.
- If the belt stops while a product is present, both sensor values remain frozen. This deliberate behavior allows the PLC jam logic to be tested.
- Changes to `conveyorRun`, `diverterGate`, and `alarmActive` are printed in the terminal.

## Setup

Create an isolated Python environment so the pinned pymodbus version does not conflict with other projects:

```powershell
cd digital_twin
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

The application waits until OpenPLC writes `TRUE` to coil 10. If port `1502` is already in use, startup stops and reports the error.

Stop the application with `Ctrl+C`.

## Test

```powershell
python -m unittest discover -s tests -v
```

The tests use Python's standard library and do not require a live PLC or Modbus client. They verify the address map, sensor values, normal product cycle, frozen sensor behavior, and monitored PLC commands.

Return to the [main project README](../README.md) for the complete startup sequence.
