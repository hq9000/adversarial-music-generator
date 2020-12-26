import os
from copy import deepcopy
from dataclasses import dataclass
from multiprocessing.pool import Pool
from typing import Optional, Dict, List

from adversarial_music_generator.interfaces import TuneFinderInterface, TuneGeneratorInterface, TuneMutatorInterface, \
    TuneEvaluatorInterface, EvaluationReducerInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.seed import Seed
from adversarial_music_generator.tune_evaluator import TuneEvaluator
from adversarial_music_generator.tune_generator import TuneGenerator

from adversarial_music_generator.tune_mutator import TuneMutator

SearchResultsDict = Dict[str, TuneEvaluationResult]
MutationSearchResultsDict = Dict[str, TuneEvaluationResult]


class TuneFinderError(Exception):
    pass


@dataclass
class GenerationSearchTask:
    base_seed_str: str
    start_idx: int
    end_idx: int
    generator: TuneGeneratorInterface
    evaluator: TuneEvaluatorInterface


@dataclass
class MutationSearchTask:
    generation_seed_strs: List[str]
    base_mutation_seed_str: str
    start_idx: int
    end_idx: int
    generator: TuneGeneratorInterface
    evaluator: TuneEvaluatorInterface
    mutator: TuneMutatorInterface


def _handle_generation_search_task(task: GenerationSearchTask) -> List[TuneEvaluationResult]:
    generator = task.generator
    evaluator = task.evaluator

    seeds: List[str] = []
    for i in range(task.start_idx, task.end_idx):
        seeds.append(task.base_seed_str + str(i))

    tunes = generator.generate_tunes(seeds)
    evaluations = evaluator.evaluate_tunes(tunes)

    if len(tunes) != len(evaluations) or len(seeds) != len(evaluations):
        raise TuneFinderError('size mismatch (error: 93bf5bcc)')

    for seed, evaluation in zip(seeds, evaluations):
        evaluation.generator_seed = seed

    return evaluations


def _handle_mutation_search_task(task: MutationSearchTask) -> SearchResultsDict:
    generator = task.generator
    evaluator = task.evaluator
    mutator = task.mutator

    source_tunes_dict: Dict[str, Tune] = {}
    for gen_seed in task.generation_seed_strs:
        source_tunes_dict[gen_seed] = generator.generate_tunes(Seed(gen_seed))

    results_dict: SearchResultsDict = {}
    for i in range(task.start_idx, task.end_idx):
        generator_seed_str = task.generation_seed_strs[i % len(task.generation_seed_strs)]
        source_tune = source_tunes_dict[generator_seed_str]

        tune_copy_for_mutation = deepcopy(source_tune)

        if i < len(task.generation_seed_strs):
            # first N tunes (one for every original seed)
            # go unmutated to leave the original
            # tunes in the evaluated set (in case no mutations bring any
            # improvement)
            mutation_seed_str = TuneMutator.SPECIAL_SEED_STR_TO_LEAVE_TUNE_UNMUTATED
        else:
            mutation_seed_str = task.base_mutation_seed_str + str(i)

        mutator.mutateTune(tune_copy_for_mutation, mutation_seed_str)

        evaluation = evaluator.evaluate_tunes(tune_copy_for_mutation)
        evaluation.generator_seed_str = generator_seed_str
        evaluation.mutator_seed_str = mutation_seed_str

        results_dict[mutation_seed_str] = evaluation

    return results_dict


class TuneFinder(TuneFinderInterface):
    def findTune(self, num_iterations: int, base_seed_str: str, generator: TuneGeneratorInterface,
                 evaluator: TuneEvaluatorInterface, mutator: TuneMutatorInterface,
                 reducer: EvaluationReducerInterface) -> Tune:

        chunk_size = 10

        random_search_tasks = self._generate_random_search_tasks(
            num_iterations=num_iterations,
            base_seed_str=base_seed_str,
            generator=generator,
            evaluator=evaluator,
            chunk_size=chunk_size
        )

        with Pool(self._get_pool_size()) as p:
            results: List[List[TuneEvaluationResult]] = p.map(_handle_generation_search_task, random_search_tasks)

        merged_results = self._merge_async_results(results)

        num_tunes_to_mutate = 4
        best_tune_evaluations: List[TuneEvaluationResult] = self._get_best_evaluations(merged_results, reducer, num_tunes_to_mutate)
        best_tunes_generation_seeds: List[str] = [x.generator_seed for x in best_tune_evaluations]

        mutation_search_tasks = self._generate_mutation_search_tasks(
            num_iterations=num_iterations,
            best_tunes_generation_seeds=best_tunes_generation_seeds,
            evaluator=evaluator,
            mutator=mutator,
            generator=generator,
            chunk_size=chunk_size,
            base_mutation_seed_str=base_seed_str
        )

        with Pool(self._get_pool_size()) as p:
            results = p.map(_handle_mutation_search_task, mutation_search_tasks)
        results_dict = self._merge_async_results(results)
        self._normalize_scores(results_dict)
        best_tune_evaluation = self._get_best_evaluations(results_dict, reducer, 1)[0]

        return self._generate_tune_by_mutation_chain(
            generator=generator,
            mutator=mutator,
            generator_seed_str=best_tune_evaluation.generator_seed_str,
            mutation_seed_str_chain=[best_tune_evaluation.mutator_seed_str])

    def _get_best_evaluations(self, evaluations: List[TuneEvaluationResult],
                              reducer: EvaluationReducerInterface, how_many: int) -> List[TuneEvaluationResult]:

        def overall_score_calculator(x: TuneEvaluationResult) -> float:
            return reducer.reduce(x)

        evaluations.sort(key=overall_score_calculator, reverse=True)
        return evaluations[0:how_many]

    def _generate_random_search_tasks(self, num_iterations: int, base_seed_str: str, generator: TuneGeneratorInterface,
                                      evaluator: TuneEvaluatorInterface, chunk_size: int) -> List[GenerationSearchTask]:
        cursor = 0
        tasks = []
        while cursor < num_iterations:
            task = GenerationSearchTask(
                start_idx=cursor,
                end_idx=min(cursor + chunk_size, num_iterations),
                generator=generator,
                evaluator=evaluator,
                base_seed_str=base_seed_str
            )
            tasks.append(task)
            cursor += chunk_size

        return tasks

    def _generate_mutation_search_tasks(self, num_iterations, best_tunes_generation_seeds: List[str],
                                        base_mutation_seed_str: str,
                                        generator: TuneGeneratorInterface, mutator: TuneMutatorInterface,
                                        evaluator: TuneEvaluatorInterface,
                                        chunk_size: int) -> List[MutationSearchTask]:
        cursor = 0
        tasks = []
        while cursor < num_iterations:
            task = MutationSearchTask(
                start_idx=cursor,
                end_idx=min(cursor + chunk_size, num_iterations),
                generator=generator,
                evaluator=evaluator,
                mutator=mutator,
                generation_seed_strs=best_tunes_generation_seeds,
                base_mutation_seed_str=base_mutation_seed_str
            )
            tasks.append(task)
            cursor += chunk_size

        return tasks

    def _merge_async_results(self, results: List[List[TuneEvaluationResult]]) -> List[TuneEvaluationResult]:
        return [val for sublist in results for val in sublist]

    def _get_pool_size(self) -> int:
        # make it dependent on the number of available CPU cores
        return 4

    def _generate_tune_by_mutation_chain(self, generator: TuneGenerator, mutator: TuneMutator, generator_seed_str: str,
                                         mutation_seed_str_chain: List[str]) -> Tune:
        tune = generator.generate_tunes(Seed(generator_seed_str))

        for seed_str in mutation_seed_str_chain:
            mutator.mutateTune(tune, seed_str)

        return tune
