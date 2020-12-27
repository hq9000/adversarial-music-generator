from abc import ABC, abstractmethod
from typing import List

from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult


class TuneGeneratorInterface(ABC):
    @abstractmethod
    def generate_tunes(self, seeds: List[str]) -> List[Tune]:
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
    def mutateTune(self, tune: Tune, seed: str):
        pass


class EvaluationReducerInterface(ABC):
    @abstractmethod
    def reduce(self, result: TuneEvaluationResult) -> float:
        pass


class TuneFinderInterface(ABC):
    @abstractmethod
    def findTune(self, num_iterations: int, base_seed_str: str, generator: TuneGeneratorInterface,
                 evaluator: TuneEvaluatorInterface, mutator: TuneMutatorInterface,
                 evaluation_reducer: EvaluationReducerInterface) -> Tune:
        pass
