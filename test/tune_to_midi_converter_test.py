import unittest

from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre_repository import TimbreRepository
from adversarial_music_generator.models.track import Track
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
        res = Tune()
        res.bpm = 123

        track1: Track = Track(TimbreRepository.lead)

        track1.notes = [
            Note(start_time_seconds=0.0, note=65, velocity=100, end_time_seconds=0.99)
        ]

        res.tracks = [track1]
        return res


if __name__ == '__main__':
    unittest.main()
