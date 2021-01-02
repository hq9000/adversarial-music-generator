import unittest

from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre_repository import TimbreRepository
from adversarial_music_generator.models.track import Track
from adversarial_music_generator.models.tune import Tune
from demo.naive_random.tune_evaluator import TuneEvaluator


class MyTestCase(unittest.TestCase):
    def test_something(self):
        evaluator = TuneEvaluator()

        tune = self._createReferenceTune(0)
        evaluation = evaluator.evaluate_tunes(tune)
        self.assertEqual(1.0, evaluation.harmony_score)

        tune = self._createReferenceTune(1)
        evaluation = evaluator.evaluate_tunes(tune)
        self.assertEqual(1.0, evaluation.harmony_score)

        tune = self._createReferenceTune(2)
        evaluation = evaluator.evaluate_tunes(tune)
        self.assertEqual(-19.0, evaluation.harmony_score)

    def _createReferenceTune(self, num_notes: int) -> Tune:
        tune = Tune()
        track = Track(TimbreRepository.lead)

        track.notes = [Note(note=65 + i, start_time_seconds=0.0, end_time_seconds=1.0, velocity=100) for i in
                       range(num_notes)]

        tune.tracks = [track]
        return tune


if __name__ == '__main__':
    unittest.main()
