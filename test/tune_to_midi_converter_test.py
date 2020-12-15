import unittest

from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.tune_to_midi_converter import TuneToMidiConverter
import os


class MyTestCase(unittest.TestCase):
    def test_something(self):
        converter = TuneToMidiConverter()
        tune = self._generateTestTune()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        converter.convert(tune, dir_path + "/output/out.mid")

    def _generateTestTune(self) -> Tune:
        pass


if __name__ == '__main__':
    unittest.main()
