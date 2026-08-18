# Modbus Address Map

This project contains two independent Modbus TCP links:

- **Python twin ↔ OpenPLC** on port `1502`: OpenPLC is the client (master), and the Python twin is the server (slave). This link represents field I/O.
- **OpenPLC ↔ Node-RED** on port `502`: Node-RED is the client, and OpenPLC is the server. This link carries operator commands and machine status.

Node-RED does not communicate directly with the twin. OpenPLC remains the single control and data path between the HMI and simulated machine.

> A Modbus signal must be identified by server, port, memory type, and address. Coil 0 on port 1502 and coil 0 on port 502 are different memory locations.

## 1. Python digital twin server

Endpoint: `127.0.0.1:1502` · Device ID: `1`

| Signal | Type | Address | Function | Direction | Meaning |
|---|---|---:|---|---|---|
| `objectDetected` | Coil | 0 | FC1 read | Twin → OpenPLC | Product present at the sensor |
| `heightReading` | Input register | 0 | FC4 read | Twin → OpenPLC | Distance in mm: empty `300`, short `220`, tall `100` |
| `conveyorRun` | Coil | 10 | FC5 write / FC1 read | OpenPLC → Twin | Belt motor command |
| `diverterGate` | Coil | 11 | FC5 write / FC1 read | OpenPLC → Twin | Diverter command for a tall product |
| `alarmActive` | Coil | 12 | FC5 write / FC1 read | OpenPLC → Twin | Jam alarm state |

The Python application updates its sensor values directly in the local datastore. OpenPLC reads those inputs and writes the actuator and alarm commands.

## 2. OpenPLC internal variables

| Variable | IEC location | Type | Source or purpose |
|---|---|---|---|
| `objectDetected` | `%IX0.0` | BOOL | Input received from `DigitalTwinIO` |
| `heightReading` | `%IW0` | INT | Input received from `DigitalTwinIO` |
| `conveyorRun` | `%QX0.0` | BOOL | Output sent to the twin |
| `diverterGate` | `%QX0.1` | BOOL | Output sent to the twin |
| `alarmActive` | `%QX0.2` | BOOL | Output sent to the twin and exposed to Node-RED |
| `startCmd` | `%QX0.3` | BOOL | Momentary HMI start command |
| `stopCmd` | `%QX0.4` | BOOL | Momentary HMI stop command |
| `resetCmd` | `%QX0.5` | BOOL | Momentary HMI alarm-reset command |
| `systemRunning` | `%QX0.6` | BOOL | Internal start/stop latch exposed to Node-RED |
| `isTallObject` | Internal | BOOL | Height-comparison result |
| `TON0` | Internal | TON | Eight-second jam timer |

The IEC locations used by the Ladder program are not automatically the same as the addresses on the Python server. `DigitalTwinIO.json` defines the mapping.

## 3. OpenPLC remote device mapping

File: `openPLC/devices/remote/DigitalTwinIO.json`

The device makes OpenPLC a Modbus TCP client of `127.0.0.1:1502`. It uses a `1000 ms` timeout, exchanges each group every `100 ms`, and retains the last received value if communication fails.

| Group | Function | Twin offset | OpenPLC location | Direction |
|---|---|---:|---|---|
| `objectDetected` | FC1 read coils | 0 | `%IX0.0` | Twin → OpenPLC |
| `heightReading` | FC4 read input registers | 0 | `%IW0` | Twin → OpenPLC |
| `conveyorRun` | FC5 write single coil | 10 | `%QX0.0` | OpenPLC → Twin |
| `diverterGate` | FC5 write single coil | 11 | `%QX0.1` | OpenPLC → Twin |
| `alarmActive` | FC5 write single coil | 12 | `%QX0.2` | OpenPLC → Twin |

For example, the PLC variable `diverterGate` is stored at `%QX0.1`; the remote-device configuration writes its value to coil 11 on the Python server.

## 4. OpenPLC Modbus server

File: `openPLC/devices/servers/Modbus.json`

OpenPLC listens on `0.0.0.0:502`. The local Node-RED flow connects to `127.0.0.1:502`, device ID `1`, and polls displayed values every `100 ms`.

| Signal | Type | Address | Function | PLC location | Node-RED use |
|---|---|---:|---|---|---|
| `conveyorRun` | Coil | 0 | FC1 read | `%QX0.0` | Belt indication |
| `diverterGate` | Coil | 1 | FC1 read | `%QX0.1` | Diverter indication |
| `alarmActive` | Coil | 2 | FC1 read | `%QX0.2` | Alarm and reset-control visibility |
| `startCmd` | Coil | 3 | FC5 write | `%QX0.3` | Start pulse |
| `stopCmd` | Coil | 4 | FC5 write | `%QX0.4` | Stop pulse |
| `resetCmd` | Coil | 5 | FC5 write | `%QX0.5` | Alarm reset pulse |
| `systemRunning` | Coil | 6 | FC1 read | `%QX0.6` | Latched running state |
| `objectDetected` | Coil | 7 | FC1 read | `%IX0.0` | Object detected indication |
| `heightReading` | Input register | 0 | FC4 read | `%IW0` | Height gauge and classification |

Start, Stop, and Reset behave like physical momentary pushbuttons. Node-RED writes `TRUE` to the corresponding coil and writes `FALSE` approximately `300 ms` later.

## 5. PLC control behavior

File: `openPLC/pous/programs/main.ld`

### Start/stop seal-in

`systemRunning = (startCmd OR systemRunning) AND NOT stopCmd AND NOT alarmActive`

The system remains latched after the Start pulse and drops when Stop or the alarm becomes active.

### Belt command

`conveyorRun` follows `systemRunning`. The remote device writes this value to coil 10 on the twin.

### Height classification

`isTallObject = heightReading < 160`

A tall simulated product reads `100 mm`; a short product reads `220 mm`; an empty belt reads `300 mm`.

### Diverter

`diverterGate = objectDetected AND isTallObject`

The gate activates only while a tall product is present.

### Jam alarm

Timer `TON0` runs while `objectDetected` remains true. After eight seconds, `alarmActive` latches and breaks the running seal-in. Resetting the alarm does not restart the conveyor; the operator must press Start again.

## 6. End-to-end examples

### Start command

1. Node-RED pulses OpenPLC coil 3 (`startCmd`).
2. The Ladder program latches `%QX0.6` (`systemRunning`).
3. `%QX0.0` (`conveyorRun`) becomes true.
4. `DigitalTwinIO` writes the value to twin coil 10.
5. The Python twin begins generating products.

### Tall-product sorting

1. The twin sets coil 0 true and input register 0 to `100`.
2. `DigitalTwinIO` maps these values to `%IX0.0` and `%IW0`.
3. The PLC classifies the product as tall because `100 < 160`.
4. The PLC sets `%QX0.1` (`diverterGate`).
5. `DigitalTwinIO` writes the command to twin coil 11.
6. Node-RED reads the updated state through OpenPLC.

### Jam detection

1. `objectDetected` remains true for eight seconds.
2. `TON0` sets and latches `alarmActive`.
3. The running latch and conveyor command drop.
4. OpenPLC sends the stopped and alarm states to the twin.
5. Node-RED displays the alarm and reset control.
6. The operator clears the condition, presses Reset Alarm, and then presses Start.
