"""Configuration and Modbus address map for the conveyor digital twin.

Keeping addresses and timing values in one place makes the simulation easy to
understand and prevents communication details from leaking into plant logic.
"""

# Network configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 1502
DEVICE_ID = 1

# Modbus coil addresses
# twin -> OpenPLC
COIL_OBJECT_DETECTED = 0

# OpenPLC -> twin
COIL_CONVEYOR_RUN = 10
COIL_DIVERTER_GATE = 11
COIL_ALARM_ACTIVE = 12

# Modbus input-register addresses (twin -> OpenPLC)
REG_HEIGHT_READING = 0

# Datastore sizes leave room for future signals without changing existing ones.
DISCRETE_INPUT_COUNT = 32
COIL_COUNT = 32
HOLDING_REGISTER_COUNT = 32
INPUT_REGISTER_COUNT = 16

# Simulated HC-SR04 readings in millimetres.
HEIGHT_BASELINE_MM = 300
HEIGHT_SHORT_MM = 220
HEIGHT_TALL_MM = 100

# Simulation timing. The original application checked stop commands every 0.2 s.
SIMULATION_STEP_SECONDS = 0.2
OBJECT_GAP_STEPS = 10       # 10 * 0.2 s = 2 s
OBJECT_PRESENT_STEPS = 20   # 20 * 0.2 s = 4 s
MONITOR_INTERVAL_SECONDS = 0.1
SERVER_STARTUP_CHECK_SECONDS = 0.2

