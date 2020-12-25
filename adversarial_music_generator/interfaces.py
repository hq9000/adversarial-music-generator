from abc import ABC, abstractmethod

from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.seed import Seed


class TuneGeneratorInterface(ABC):
    @abstractmethod
    def generateTune(self, seed: Seed) -> Tune:
        return Tune()


class TuneEvaluatorInterface(ABC):
    @abstractmethod
    def evaluate(self, tune: Tune) -> TuneEvaluationResult:
        pass


class TuneMutatorInterface(ABC):
    @abstractmethod
    def mutateTune(self, tune: Tune, seed_str: str):
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
