import unittest

from adversarial_music_generator.seed import Seed
from adversarial_music_generator.tune_finder import TuneFinder
from adversarial_music_generator.tune_generator import TuneGenerator


class TuneGeneratorTestCase(unittest.TestCase):
    def test_something(self):
        generator = TuneGenerator()
        tune = generator.generateTune(Seed("123"))


if __name__ == '__main__':
    unittest.main()
