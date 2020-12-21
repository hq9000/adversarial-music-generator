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

        interval = abs(this_note.note - that_note.note) % 12

        disharmony_map = {
            0: 0,
            1: 10,
            2: 6,
            3: 2,
            4: 3,
            5: 1,
            6: 4,
            7: 7,
            8: 4,
            9: 2,
            10: 8,
            11: 10
        }

        return disharmony_map[interval] * overlapping_length

    def _calculate_overlapping_length(self, a: Note, b: Note) -> float:
        return max(0.0, min(a.end_time_seconds, b.end_time_seconds) - max(a.start_time_seconds, b.start_time_seconds))

    def _evaluate_content(self, tune: Tune):
        expected_mean_num_notes = 20
        diff = tune.num_notes - expected_mean_num_notes
        return 1.0 - abs(diff)
