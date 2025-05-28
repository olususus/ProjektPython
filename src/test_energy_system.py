import unittest
# src/test_energy_system.py
from src.energy_system import calculate_energy_interval

class TestEnergySystem(unittest.TestCase):
    def test_intervals(self):
        self.assertEqual(calculate_energy_interval(True, True, True), 1.0)
        self.assertEqual(calculate_energy_interval(True, True, False), 1.5)
        self.assertEqual(calculate_energy_interval(True, False, True), 1.5)
        self.assertEqual(calculate_energy_interval(True, False, False), 3.0)
        self.assertEqual(calculate_energy_interval(False, True, True), 1.5)
        self.assertEqual(calculate_energy_interval(False, True, False), 2.0)
        self.assertEqual(calculate_energy_interval(False, False, True), 2.0)
        self.assertEqual(calculate_energy_interval(False, False, False), None)

if __name__ == '__main__':
    unittest.main()
