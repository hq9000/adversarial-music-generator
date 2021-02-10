import unittest
from typing import List
import re

from adversarial_music_generator.find_tunes_task import FindTunesTask
from adversarial_music_generator.interfaces import TuneGeneratorInterface, TuneEvaluatorInterface, TuneMutatorInterface, \
    EvaluationReducerInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre_repository import TimbreRepository
from adversarial_music_generator.models.track import Track
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.tune_finder import Tune, TuneFinder
from parameterized import parameterized


class MockTuneGenerator(TuneGeneratorInterface):
    def generate_tunes(self, generator_seed: str, tune_seeds: List[str]) -> List[Tune]:
        return [self._generate_one_tune(s) for s in tune_seeds]

    def _generate_one_tune(self, seed: str) -> Tune:
        # tune_seed is expected to end up with a number,
        # this number we use to generate that many notes

        only_digits = re.sub(r"\D", "", seed)
        num_notes = int(only_digits)

        track = Track(TimbreRepository.lead)
        notes = []
        for i in range(num_notes):
            notes.append(Note(note=65, start_time_seconds=0.0, end_time_seconds=1.0, velocity=100))

        track.notes = notes

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
        if seed == TuneMutatorInterface.SPECIAL_SEED_STR_TO_LEAVE_TUNE_UNMUTATED:
            return

        only_digits = re.sub(r"\D", "", seed)
        num_additional_notes = int(only_digits)
        track = tune.tracks[0]
        for i in range(num_additional_notes):
            note = Note(note=65 + i, start_time_seconds=0.0, end_time_seconds=1.0, velocity=100)
            track.notes.append(note)


class MockReducer(EvaluationReducerInterface):
    def reduce(self, result: TuneEvaluationResult) -> float:
        return result.get_aspect_value(TuneFinderTestCase.ASPECT_NUM_NOTES)


class TuneFinderTestCase(unittest.TestCase):
    """
    In this test case we use some very predictable generator, mutator, evaluator, and reducer.

    1. tune_seeds produced by the finder have numeric parts. and that part is used to
       define the following things:
       - how many notes are generated by generator
       - how many notes are added by mutator
    2. evaluation is simple, there is only one evaluation aspect called "number of notes" and it is, quite simply,
       equal to... well... number of notes in the tune
    3. reducer does nothing at all but returning the raw aspect value

    this setup enables us to expect that the tune with the most notes (added during the "biggest" generation and "biggets" mutation)
    will be the best one, and this we can assert.
    """

    ASPECT_NUM_NOTES = "num_notes"

    @parameterized.expand(
        [
            (True, 10),
            (False, 10),
            (True, 1000),
            (False, 1000),
        ]
    )
    def test_find(self, parallelize: bool, chunk_size: int):
        tune_finder = TuneFinder()

        generator, evaluator = self._create_generator(), self._create_evaluator()
        reducer = self._create_reducer()
        mutator = self._create_mutator()

        task = FindTunesTask(
            num_generation_iterations=100,
            num_mutation_epochs=2,
            num_mutation_iterations_in_epoch=100,
            num_tunes_to_keep_after_mutation_epoch=10,
            num_tunes_to_keep_from_generation=4,
            generator=generator,
            mutator=mutator,
            reducer=reducer,
            evaluator=evaluator,
            num_tunes_to_find=1,
            base_seed="a",
            parallelize=parallelize,
            chunk_size=chunk_size
        )

        tunes = tune_finder.find_tunes(task)

        self.assertEqual(1, len(tunes))
        self.assertEqual(388, len(tunes[0].tracks[0].notes))

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
