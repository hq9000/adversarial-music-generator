import unittest
import pyximport
from parameterized import parameterized

pyximport.install()
from adversarial_music_generator.evaluation_lib.harmony import calculate_disharmony

from array import array


class TuneFinderTestCase(unittest.TestCase):

    @parameterized.expand(
        [
            (array('f', [0.0, 2.0]), array('f', [0.5, 2.5]), array('i', [1, 2]), 0.0),
            (array('f', [0.0, 0.0]), array('f', [0.5, 0.5]), array('i', [1, 2]), 20.0),
            (array('f', [0.0, 0.0]), array('f', [1.0, 1.0]), array('i', [1, 2]), 25.0)
        ]
    )
    def test_something(self, starts: array, ends: array, pitches: array, expected_result: float):
        res = calculate_disharmony(starts, ends, pitches)
        self.assertEqual(expected_result, res)
