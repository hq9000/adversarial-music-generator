from copy import deepcopy
from dataclasses import dataclass
from multiprocessing.pool import Pool
from typing import Dict, List, Iterable

from adversarial_music_generator.find_tunes_task import FindTunesTask
from adversarial_music_generator.interfaces import TuneFinderInterface, TuneGeneratorInterface, TuneMutatorInterface, \
    TuneEvaluatorInterface, EvaluationReducerInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult

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

    seeds = [task.base_seed_str + str(i) for i in range(task.start_idx, task.end_idx)]

    tunes = generator.generate_tunes(seeds)
    evaluations = evaluator.evaluate_tunes(tunes)

    if len(tunes) != len(evaluations) or len(seeds) != len(evaluations):
        raise TuneFinderError('size mismatch (error: 93bf5bcc)')

    for seed, evaluation in zip(seeds, evaluations):
        evaluation.generator_seed = seed

    return evaluations


def _handle_mutation_search_task(task: MutationSearchTask) -> List[TuneEvaluationResult]:
    generator = task.generator
    evaluator = task.evaluator
    mutator = task.mutator

    source_tunes = generator.generate_tunes(task.generation_seed_strs)
    source_tunes_dict = {gen_seed: tune for (gen_seed, tune) in zip(task.generation_seed_strs, source_tunes)}

    mutated_tunes: List[Tune] = []
    for i in range(task.start_idx, task.end_idx):
        source_tune_seed = task.generation_seed_strs[i % len(task.generation_seed_strs)]
        source_tune = source_tunes_dict[source_tune_seed]
        tune_copy_for_mutation = deepcopy(source_tune)

        if i >= len(task.generation_seed_strs):
            # first N tunes (one for every original seed)
            # go unmutated to leave the original
            # tunes in the evaluated set (in case no mutations bring any
            # improvement)
            mutation_seed = task.base_mutation_seed_str + str(i)
            mutator.mutate_tune(tune_copy_for_mutation, mutation_seed)
        mutated_tunes.append(tune_copy_for_mutation)
    return evaluator.evaluate_tunes(mutated_tunes)


class TuneFinder(TuneFinderInterface):
    def findTune(self, find_task: FindTunesTask) -> Iterable[Tune]:

        chunk_size = 10  # normally, it should depend on the number of CPU cores

        random_search_tasks = self._generate_random_search_tasks(
            num_iterations=find_task.num_generation_iterations,
            base_seed_str=find_task.base_seed,
            generator=find_task.generator,
            evaluator=find_task.evaluator,
            chunk_size=chunk_size
        )

        # performing generation using a pool of workers
        with Pool(self._get_pool_size()) as p:
            results: List[List[TuneEvaluationResult]] = p.map(_handle_generation_search_task, random_search_tasks)

        merged_results = self._merge_async_results(results)

        num_tunes_to_mutate = find_task.num_tunes_to_mutate
        best_tune_evaluations: List[TuneEvaluationResult] = self._get_best_evaluations(merged_results,
                                                                                       find_task.reducer,
                                                                                       num_tunes_to_mutate)
        best_tunes_generation_seeds: List[str] = [x.generator_seed for x in best_tune_evaluations]

        mutation_search_tasks = self._generate_mutation_search_tasks(
            num_iterations=find_task.num_mutation_iterations,
            best_tunes_generation_seeds=best_tunes_generation_seeds,
            evaluator=find_task.evaluator,
            mutator=find_task.mutator,
            generator=find_task.generator,
            chunk_size=chunk_size,
            base_mutation_seed_str=find_task.base_seed
        )

        with Pool(self._get_pool_size()) as p:
            results = p.map(_handle_mutation_search_task, mutation_search_tasks)

        mutation_results = self._merge_async_results(results)
        best_tune_evaluations = self._get_best_evaluations(mutation_results, find_task.reducer,
                                                           find_task.num_tunes_to_find)

        res: List[Tune] = []
        for i in range(find_task.num_tunes_to_find):
            res.append(self._generate_tune_by_mutation_chain(
                generator=find_task.generator,
                mutator=find_task.mutator,
                generator_seed_str=best_tune_evaluations[i].generator_seed,
                mutation_seed_str_chain=best_tune_evaluations[i].mutator_seeds)
            )

        return res

    def _get_best_evaluations(self, evaluations: List[TuneEvaluationResult],
                              reducer: EvaluationReducerInterface,
                              how_many: int) -> List[TuneEvaluationResult]:

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

    def _generate_tune_by_mutation_chain(self, generator: TuneGeneratorInterface, mutator: TuneMutatorInterface,
                                         generator_seed_str: str,
                                         mutation_seed_str_chain: List[str]) -> Tune:
        tunes = generator.generate_tunes([generator_seed_str])

        tune = tunes[0]

        for seed_str in mutation_seed_str_chain:
            mutator.mutate_tune(tune, seed_str)

        return tune
