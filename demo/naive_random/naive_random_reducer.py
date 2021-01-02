from adversarial_music_generator.interfaces import EvaluationReducerInterface
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult


class NaiveRandomReducer(EvaluationReducerInterface):
    def reduce(self, result: TuneEvaluationResult) -> float:
        result = cast(Nai)

