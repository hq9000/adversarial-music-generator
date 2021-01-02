from adversarial_music_generator.interfaces import EvaluationReducerInterface
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.demo.naive_random.naive_random_evaluator import NaiveRandomEvaluator


class NaiveRandomReducer(EvaluationReducerInterface):
    def reduce(self, result: TuneEvaluationResult) -> float:
        r = result.get_aspect_value(NaiveRandomEvaluator.ASPECT_RHYTHMICALITY)
        h = result.get_aspect_value(NaiveRandomEvaluator.ASPECT_HARMONY)
        c = result.get_aspect_value(NaiveRandomEvaluator.ASPECT_CONTENT)

        return 2 * h + c + r
