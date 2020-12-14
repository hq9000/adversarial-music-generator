from abc import ABC

from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult


class TuneEvaluator(ABC):
    def evaluate(self, tune: Tune) -> TuneEvaluationResult:
        pass
