from dataclasses import dataclass
from adversarial_music_generator.interfaces import TuneGeneratorInterface, TuneEvaluatorInterface, \
    EvaluationReducerInterface, TuneMutatorInterface, TuneProcessorInterface


@dataclass
class FindTunesTask:
    generator: TuneGeneratorInterface
    evaluator: TuneEvaluatorInterface
    postprocessor: TuneProcessorInterface
    reducer: EvaluationReducerInterface
    mutator: TuneMutatorInterface
    num_generation_iterations: int
    num_mutation_epochs: int
    num_tunes_to_keep_from_generation: int
    num_tunes_to_keep_after_mutation_epoch: int
    num_mutation_iterations_in_epoch: int
    num_tunes_to_find: int
    base_seed: str
    parallelize: bool = True
    chunk_size: int = 1000
