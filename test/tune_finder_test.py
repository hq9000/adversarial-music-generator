import os
import unittest

from adversarial_music_generator.interfaces import TuneGeneratorInterface, TuneEvaluatorInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre_repository import TimbreRepository
from adversarial_music_generator.models.track import Track
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.seed import Seed
from adversarial_music_generator.tune_finder import TuneFinder
from adversarial_music_generator.tune_to_midi_converter import TuneToMidiConverter


class TuneFinderTestCase(unittest.TestCase):
    def test_something(self):
        tune_finder = TuneFinder()
        seed = 'whatever1'
        num_iterations = 60

        generator = self._create_generator()
        evaluator = self._create_evaluator()

        tune = tune_finder.findTune(num_iterations, seed)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        converter = TuneToMidiConverter()
        converter.convert(tune, dir_path + "/output/out_" + seed + "_" + str(num_iterations) + ".mid")

    def _create_generator(self) -> TuneGeneratorInterface:
        class MockTuneGenerator(TuneGeneratorInterface):
            def generateTune(self, seed: Seed) -> Tune:
                track = Track(TimbreRepository.lead)
                track.notes = [Note(note=65, start_time_seconds=0.0, end_time_seconds=1.0, velocity=100)]
                tune = Tune()
                tune.tracks = [track]
                return tune

        return MockTuneGenerator()

    def _create_evaluator(self) -> TuneEvaluatorInterface:
        class MockTuneEvaluator(TuneEvaluatorInterface):
            def evaluate(self, tune: Tune) -> TuneEvaluationResult:
                pass

        return MockTuneEvaluator()


if __name__ == '__main__':
    unittest.main()
