import unittest

from year_2021.day_19.solution import Point, Bounds

class BoundsTest(unittest.TestCase):
    def test_get_bounds(self):
        self.assertEqual(
            Bounds.get_bounds([Point(0,0)]),
            Bounds(0, 0, 0, 0),
        )
        self.assertEqual(
            Bounds.get_bounds([Point(10, 100), Point(100, 10)]),
            Bounds(10, 10, 100, 100),
        )
