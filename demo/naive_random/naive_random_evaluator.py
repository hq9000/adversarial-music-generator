from typing import List, Optional, Dict

from adversarial_music_generator.interfaces import TuneEvaluatorInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from demo.naive_random.naive_random_generator import NaiveRandomGenerator


class NaiveRandomEvaluator(TuneEvaluatorInterface):
    ASPECT_RHYTHMICALITY = 'rhythmicality'
    ASPECT_HARMONY = 'harmony'
    ASPECT_CONTENT = 'content'

    def __init__(self):
        self._calibrated: bool = False
        self._min_calibration_values: Dict[str, float] = {}
        self._max_calibration_values: Dict[str, float] = {}
        self._has_to_calibrate: bool = True

    def get_aspects(self) -> List[str]:
        return [
            self.ASPECT_RHYTHMICALITY,
            self.ASPECT_HARMONY,
            self.ASPECT_CONTENT
        ]

    def evaluate_tunes(self, tunes: List[Tune]) -> List[TuneEvaluationResult]:

        if self._has_to_calibrate:
            if not self._calibrated:
                self._calibrate()

        return [self._evaluate_one_tune(tune) for tune in tunes]

    def _evaluate_one_tune(self, tune: Tune) -> TuneEvaluationResult:
        res = TuneEvaluationResult()

        res.set_aspect_value(self.ASPECT_HARMONY, self._evaluate_harmony(tune))
        res.set_aspect_value(self.ASPECT_RHYTHMICALITY, self._evaluate_rhythmicality(tune))
        res.set_aspect_value(self.ASPECT_CONTENT, self._evaluate_content(tune))

        if self._has_to_calibrate:
            for aspect in self.get_aspects():
                raw_value = res.get_aspect_value(aspect)
                min_value = self._min_calibration_values[aspect]
                max_value = self._max_calibration_values[aspect]

                if min_value == max_value:
                    normalized_value = min_value  # this is actually an error
                else:
                    normalized_value = (raw_value - min_value) / (max_value - min_value)

                res.set_aspect_value(aspect, normalized_value)

        return res

    def _evaluate_harmony(self, tune: Tune) -> float:
        res = 1.0

        for this_note in tune.all_notes():
            for that_note in tune.all_notes():
                if this_note is not that_note:
                    res -= self._calculate_amount_of_disharmony_of_two_notes(this_note, that_note)

        return res

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

    def _calibrate(self):

        generator = NaiveRandomGenerator()

        seeds = ['calibrate' + str(i) for i in range(100)]
        tunes = generator.generate_tunes(seeds)

        self._has_to_calibrate = False

        non_normalized_evaluations = self.evaluate_tunes(tunes)

        for evaluation in non_normalized_evaluations:
            for aspect in self.get_aspects():

                value = evaluation.get_aspect_value(aspect)

                if aspect not in self._min_calibration_values:
                    self._min_calibration_values[aspect] = value

                if aspect not in self._max_calibration_values:
                    self._max_calibration_values[aspect] = value

                self._min_calibration_values[aspect] = min(value, self._min_calibration_values[aspect])
                self._max_calibration_values[aspect] = max(value, self._max_calibration_values[aspect])

        self._has_to_calibrate = True
