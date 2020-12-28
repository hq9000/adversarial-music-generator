import os
import unittest
from typing import List

from adversarial_music_generator.interfaces import TuneGeneratorInterface, TuneEvaluatorInterface, TuneMutatorInterface, \
    EvaluationReducerInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre_repository import TimbreRepository
from adversarial_music_generator.models.track import Track
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.seed import Seed
from adversarial_music_generator.tune_finder import TuneFinder
from adversarial_music_generator.tune_to_midi_converter import TuneToMidiConverter


class MockTuneGenerator(TuneGeneratorInterface):
    def generate_tunes(self, seeds: List[str]) -> List[Tune]:
        return [self._generate_one_tune(s) for s in seeds]

    def _generate_one_tune(self, seed: str) -> Tune:
        track = Track(TimbreRepository.lead)
        track.notes = [Note(note=65, start_time_seconds=0.0, end_time_seconds=1.0, velocity=100)]
        tune = Tune()
        tune.tracks = [track]
        return tune


class MockTuneEvaluator(TuneEvaluatorInterface):
    def get_aspects(self) -> List[str]:
        return [
            TuneFinderTestCase.ASPECT_NUM_NOTES
        ]

    def evaluate_tunes(self, tunes: List[Tune]) -> List[TuneEvaluationResult]:
        return [self._evaluate_one_tune(t) for t in tunes]

    def _evaluate_one_tune(self, tune: Tune) -> TuneEvaluationResult:
        res = TuneEvaluationResult()

        count = 0
        for note in tune.all_notes():
            count += 1

        res.set_aspect_value(TuneFinderTestCase.ASPECT_NUM_NOTES, float(count))
        return res


class MockTuneMutator(TuneMutatorInterface):
    def mutate_tune(self, tune: Tune, seed: str):
        seed_obj = Seed(seed)
        num_additional_notes = seed_obj.randint(3, 5, 'num additional notes')
        track = tune.tracks[0]
        for i in range(num_additional_notes):
            note = Note(note=65 + i, start_time_seconds=0.0, end_time_seconds=1.0, velocity=100)
            track.notes.append(note)


class MockReducer(EvaluationReducerInterface):
    def reduce(self, result: TuneEvaluationResult) -> float:
        return result.get_aspect_value(TuneFinderTestCase.ASPECT_NUM_NOTES)


class TuneFinderTestCase(unittest.TestCase):
    ASPECT_NUM_NOTES = "num_notes"

    def test_something(self):
        tune_finder = TuneFinder()
        seed = 'whatever1'
        num_iterations = 60

        generator, evaluator = self._create_generator(), self._create_evaluator()
        reducer = self._create_reducer()
        mutator = self._create_mutator()

        tune = tune_finder.findTune(
            num_iterations=num_iterations,
            base_seed_str='a',
            generator=generator,
            evaluator=evaluator,
            reducer=reducer,
            mutator=mutator
        )

        dir_path = os.path.dirname(os.path.realpath(__file__))
        converter = TuneToMidiConverter()
        converter.convert(tune, dir_path + "/output/out_" + seed + "_" + str(num_iterations) + ".mid")

    def _create_generator(self) -> TuneGeneratorInterface:
        return MockTuneGenerator()

    def _create_evaluator(self) -> TuneEvaluatorInterface:
        return MockTuneEvaluator()

    def _create_mutator(self) -> TuneMutatorInterface:
        return MockTuneMutator()

    def _create_reducer(self) -> EvaluationReducerInterface:
        return MockReducer()


if __name__ == '__main__':
    unittest.main()
