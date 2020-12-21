from adversarial_music_generator.interfaces import TuneEvaluatorInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult


class TuneEvaluator(TuneEvaluatorInterface):
    def evaluate(self, tune: Tune) -> TuneEvaluationResult:
        res = TuneEvaluationResult()

        res.harmony_score = self._evaluate_harmony(tune)
        res.rhythmicality_score = self._evaluate_rhythmicality(tune)
        res.content_score = self._evaluate_content(tune)

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
