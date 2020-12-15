from adversarial_music_generator.interfaces import TuneEvaluatorInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult


class TuneEvaluator(TuneEvaluatorInterface):
    def evaluate(self, tune: Tune) -> TuneEvaluationResult:
        return TuneEvaluationResult()
