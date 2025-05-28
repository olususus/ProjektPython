import unittest
# src/test_stats.py
import unittest
import os
from src.stats import load_stats, save_stats, update_stats

class TestStats(unittest.TestCase):
    def setUp(self):
        self.stats_file = os.path.join(os.path.dirname(__file__), '../stats.json')
        if os.path.exists(self.stats_file):
            os.remove(self.stats_file)

    def tearDown(self):
        if os.path.exists(self.stats_file):
            os.remove(self.stats_file)

    def test_update_stats_survived(self):
        update_stats(2, True)
        stats = load_stats()
        self.assertEqual(stats['nights_survived'], 1)
        self.assertEqual(stats['max_night'], 2)

    def test_update_stats_death(self):
        update_stats(1, False)
        stats = load_stats()
        self.assertEqual(stats['deaths'], 1)

if __name__ == '__main__':
    unittest.main()
