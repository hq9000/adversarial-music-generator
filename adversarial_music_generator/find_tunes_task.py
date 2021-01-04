from dataclasses import dataclass
from typing import Optional

from adversarial_music_generator.interfaces import TuneGeneratorInterface, TuneEvaluatorInterface, \
    EvaluationReducerInterface, TuneMutatorInterface


@dataclass
class FindTunesTask:
    generator: TuneGeneratorInterface
    evaluator: TuneEvaluatorInterface
    reducer: EvaluationReducerInterface
    mutator: TuneMutatorInterface
    num_generation_iterations: int
    num_tunes_to_mutate: int
    num_mutation_iterations: int
    num_tunes_to_find: int
    base_seed: str
    parallelize: bool = True
