from abc import ABC, abstractmethod
from typing import List, Dict

from adversarial_music_generator.interfaces import TuneEvaluatorInterface, TuneGeneratorInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult


class CalibratingTuneEvaluator(TuneEvaluatorInterface, ABC):

    def __init__(self, generator_for_calibration: TuneGeneratorInterface, generator_seed_for_calibration: str, num_calibration_iterations: int = 100):
        self._calibrated: bool = False
        self._generator_for_calibration: TuneGeneratorInterface = generator_for_calibration
        self._generator_seed_for_calibration: str = generator_seed_for_calibration
        self._min_calibration_values: Dict[str, float] = {}
        self._max_calibration_values: Dict[str, float] = {}
        self._num_calibration_iterations: int = num_calibration_iterations

    def evaluate_tunes(self, tunes: List[Tune]) -> List[TuneEvaluationResult]:
        if not self._calibrated:
            self._calibrate(self._generator_for_calibration)
            self._calibrated = True

        evaluations = [self._evaluate_one_tune_without_normalization(tune) for tune in tunes]
        [self._normalize_evaluation(x) for x in evaluations]

        return evaluations

    def _calibrate(self, generator: TuneGeneratorInterface) -> None:

        seeds = ['calibrate' + str(i) for i in range(self._num_calibration_iterations)]
        tunes = generator.generate_tunes(self._generator_seed_for_calibration, seeds)

        not_normalized_evaluations = [self._evaluate_one_tune_without_normalization(x) for x in tunes]

        for evaluation in not_normalized_evaluations:
            for aspect in self.get_aspects():

                value = evaluation.get_aspect_value(aspect)

                if aspect not in self._min_calibration_values:
                    self._min_calibration_values[aspect] = value

                if aspect not in self._max_calibration_values:
                    self._max_calibration_values[aspect] = value

                self._min_calibration_values[aspect] = min(value, self._min_calibration_values[aspect])
                self._max_calibration_values[aspect] = max(value, self._max_calibration_values[aspect])

    @abstractmethod
    def _evaluate_one_tune_without_normalization(self, tune: Tune) -> TuneEvaluationResult:
        pass

    def _normalize_evaluation(self, evaluation: TuneEvaluationResult):
        for aspect in self.get_aspects():
            raw_value = evaluation.get_aspect_value(aspect)
            min_value = self._min_calibration_values[aspect]
            max_value = self._max_calibration_values[aspect]

            if min_value == max_value:
                normalized_value = min_value  # this is actually an error
            else:
                normalized_value = (raw_value - min_value) / (max_value - min_value)

            evaluation.set_aspect_value(aspect, normalized_value)
