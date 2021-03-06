from abc import ABC, abstractmethod
from typing import List

from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult


class TuneGeneratorInterface(ABC):
    @abstractmethod
    def generate_tunes(self, generator_seed: str, tune_seeds: List[str]) -> List[Tune]:
        pass


class TuneEvaluatorInterface(ABC):

    @abstractmethod
    def get_aspects(self) -> List[str]:
        pass

    @abstractmethod
    def evaluate_tunes(self, tunes: List[Tune]) -> List[TuneEvaluationResult]:
        pass


class TuneMutatorInterface(ABC):
    SPECIAL_SEED_STR_TO_LEAVE_TUNE_UNMUTATED = 'transparent'

    @abstractmethod
    def mutate_tune(self, tune: Tune, seed: str):
        pass


class EvaluationReducerInterface(ABC):
    @abstractmethod
    def reduce(self, result: TuneEvaluationResult) -> float:
        pass


class TuneProcessorInterface(ABC):

    @abstractmethod
    def process(self, tune: Tune, base_seed: str, tune_seed: str):
        pass
