from array import array
from typing import List

from pyximport import pyximport

from adversarial_music_generator.calibrating_tune_evaluator import CalibratingTuneEvaluator
from adversarial_music_generator.interfaces import TuneGeneratorInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult

pyximport.install()
from adversarial_music_generator.evaluation_lib.harmony import calculate_disharmony


class NaiveRandomEvaluator(CalibratingTuneEvaluator):
    ASPECT_RHYTHMICALITY = 'rhythmicality'
    ASPECT_HARMONY = 'harmony'
    ASPECT_CONTENT = 'content'

    def __init__(self, generator_for_calibration: TuneGeneratorInterface):
        super().__init__(generator_for_calibration)

    def get_aspects(self) -> List[str]:
        return [
            self.ASPECT_RHYTHMICALITY,
            self.ASPECT_HARMONY,
            self.ASPECT_CONTENT
        ]

    def _evaluate_one_tune_without_normalization(self, tune: Tune) -> TuneEvaluationResult:
        res = TuneEvaluationResult()

        # res.set_aspect_value(self.ASPECT_HARMONY, self._evaluate_harmony(tune))
        res.set_aspect_value(self.ASPECT_HARMONY, self._evaluate_harmony_optimized(tune))
        res.set_aspect_value(self.ASPECT_RHYTHMICALITY, self._evaluate_rhythmicality(tune))
        res.set_aspect_value(self.ASPECT_CONTENT, self._evaluate_content(tune))
        return res

    def _evaluate_harmony(self, tune: Tune) -> float:
        res = 1.0

        for this_note in tune.all_notes():
            for that_note in tune.all_notes():
                if this_note is not that_note:
                    res -= self._calculate_amount_of_disharmony_of_two_notes(this_note, that_note)

        return res

    def _evaluate_harmony_optimized(self, tune: Tune) -> float:
        num_notes = tune.num_notes

        starts = array('f', [0.0] * num_notes)
        ends = array('f', [0.0] * num_notes)
        pitches = array('i', [0] * num_notes)

        for i, note in enumerate(tune.all_notes()):
            starts[i] = note.start_time_seconds
            ends[i] = note.end_time_seconds
            pitches[i] = note.note

        return 1.0 - calculate_disharmony(starts, ends, pitches)

    def _evaluate_rhythmicality(self, tune: Tune) -> float:
        res = 1.0
        return res

    def _calculate_amount_of_disharmony_of_two_notes(self, this_note: Note, that_note: Note) -> float:

        overlapping_length = self._calculate_overlapping_length(this_note, that_note)
        if overlapping_length == 0.0:
            return 0.0

        interval = abs(this_note.note - that_note.note) % 12

        disharmony_map = {
            0: 0,  # C
            1: 10,  # C#
            2: 3,  # D
            3: 3,  # D#
            4: 2,  # E
            5: 1,  # F
            6: 10,  # F#
            7: 1,  # G
            8: 3,  # G#
            9: 6,  # A
            10: 3,  # A#
            11: 10  # B
        }

        return disharmony_map[interval] * overlapping_length

    def _calculate_overlapping_length(self, a: Note, b: Note) -> float:
        return max(0.0, min(a.end_time_seconds, b.end_time_seconds) - max(a.start_time_seconds, b.start_time_seconds))

    def _evaluate_content(self, tune: Tune):
        expected_mean_num_notes = 20
        diff = tune.num_notes - expected_mean_num_notes
        return 1.0 - abs(diff)
