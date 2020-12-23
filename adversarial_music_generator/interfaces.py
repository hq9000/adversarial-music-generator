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


class TuneFinderInterface(ABC):
    @abstractmethod
    def findTune(self, num_iterations: int, seed_str: str) -> Tune:
        pass


class TuneMutatorInterface(ABC):
    @abstractmethod
    def mutateTune(self, generator: TuneGeneratorInterface, num_iterations: int, tune_seed: str):
        pass
