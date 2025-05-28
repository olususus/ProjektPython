import unittest

# src/test_animatronic_ai.py
from src.animatronic_ai import AnimatronicAI

class TestAnimatronicAI(unittest.TestCase):
    def test_move_probability(self):
        ai = AnimatronicAI('chica', 20, 0.01, 20, [5,4,3,2,1,'door'])
        ai.active = True
        ai.position = -1
        # Przy AI=20 i move_range=20, po 100 ruchach powinna być w drzwiach
        for _ in range(100):
            ai.try_move()
        self.assertTrue(ai.position >= 0)

    def test_reset(self):
        ai = AnimatronicAI('bonnie', 10, 0.01, 20, [5,4,3,2,1,'door'])
        ai.position = 3
        ai.reset()
        self.assertEqual(ai.position, -1)

if __name__ == '__main__':
    unittest.main()
