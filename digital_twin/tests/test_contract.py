"""Regression tests for the public Modbus and timing contract."""

import unittest

import config


class ConfigurationContractTests(unittest.TestCase):
    def test_network_interface_is_preserved(self) -> None:
        self.assertEqual(config.SERVER_IP, "127.0.0.1")
        self.assertEqual(config.SERVER_PORT, 1502)
        self.assertEqual(config.DEVICE_ID, 1)

    def test_modbus_address_map_is_preserved(self) -> None:
        self.assertEqual(config.COIL_OBJECT_DETECTED, 0)
        self.assertEqual(config.COIL_CONVEYOR_RUN, 10)
        self.assertEqual(config.COIL_DIVERTER_GATE, 11)
        self.assertEqual(config.COIL_ALARM_ACTIVE, 12)
        self.assertEqual(config.REG_HEIGHT_READING, 0)

    def test_sensor_values_and_timings_are_preserved(self) -> None:
        self.assertEqual(config.HEIGHT_BASELINE_MM, 300)
        self.assertEqual(config.HEIGHT_SHORT_MM, 220)
        self.assertEqual(config.HEIGHT_TALL_MM, 100)
        self.assertEqual(
            config.OBJECT_GAP_STEPS * config.SIMULATION_STEP_SECONDS,
            2.0,
        )
        self.assertEqual(
            config.OBJECT_PRESENT_STEPS * config.SIMULATION_STEP_SECONDS,
            4.0,
        )


if __name__ == "__main__":
    unittest.main()

