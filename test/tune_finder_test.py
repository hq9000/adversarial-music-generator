import os
import unittest
from typing import List

from adversarial_music_generator.interfaces import TuneGeneratorInterface, TuneEvaluatorInterface, TuneMutatorInterface
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
            def generate_tunes(self, seed: Seed) -> Tune:
                track = Track(TimbreRepository.lead)
                track.notes = [Note(note=65, start_time_seconds=0.0, end_time_seconds=1.0, velocity=100)]
                tune = Tune()
                tune.tracks = [track]
                return tune

        return MockTuneGenerator()

    def _create_evaluator(self) -> TuneEvaluatorInterface:
        class MockTuneEvaluator(TuneEvaluatorInterface):
            def get_aspects(self) -> List[str]:
                return [
                    'num_notes'
                ]

            def evaluate_tunes(self, tune: Tune) -> TuneEvaluationResult:
                res = TuneEvaluationResult()

                count = 0
                for note in tune.all_notes():
                    count += 1

                res.set_aspect_value('num_notes', float(count))
                return res

        return MockTuneEvaluator()

    def _create_mutator(self) -> TuneMutatorInterface:
        class MockTuneMutator(TuneMutatorInterface):
            def mutateTune(self, tune: Tune, seed: str):
                seed_obj = Seed(seed)
                num_additional_notes = seed_obj.randint(3,5, 'num additional notes')
                tune


        return MockTuneMutator()

if __name__ == '__main__':
    unittest.main()
