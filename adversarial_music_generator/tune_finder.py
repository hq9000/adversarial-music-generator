import os
from copy import deepcopy
from dataclasses import dataclass
from math import ceil
from multiprocessing.pool import Pool
from pprint import pprint
from typing import Optional, Dict, List, Callable

from adversarial_music_generator.interfaces import TuneFinderInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.seed import Seed
from adversarial_music_generator.tune_evaluator import TuneEvaluator
from adversarial_music_generator.tune_generator import TuneGenerator
import multiprocessing as mp

from adversarial_music_generator.tune_mutator import TuneMutator

SearchResultsDict = Dict[str, TuneEvaluationResult]
MutationSearchResultsDict = Dict[str, TuneEvaluationResult]


@dataclass
class GenerationSearchTask:
    base_seed_str: str
    start_idx: int
    end_idx: int
    generator: TuneGenerator
    evaluator: TuneEvaluator


@dataclass
class MutationSearchTask:
    generation_seed_strs: List[str]
    base_mutation_seed_str: str
    start_idx: int
    end_idx: int
    generator: TuneGenerator
    evaluator: TuneEvaluator
    mutator: TuneMutator


def _handle_generation_search_task(task: GenerationSearchTask) -> SearchResultsDict:
    # print(os.getpid(), "start")

    generator = task.generator
    evaluator = task.evaluator

    results_dict: SearchResultsDict = {}
    max_harmony = None
    for i in range(task.start_idx, task.end_idx):
        if i % 10 == 0:
            print(os.getpid(), str(i), str(max_harmony))
        sequence_seed_str = task.base_seed_str + str(i)
        seed = Seed(sequence_seed_str)
        tune = generator.generateTune(seed)
        evaluation = evaluator.evaluate(tune)

        if max_harmony is None:
            max_harmony = evaluation.harmony_score

        max_harmony = max(max_harmony, evaluation.harmony_score)

        evaluation.generator_seed_str = sequence_seed_str
        results_dict[sequence_seed_str] = evaluation

    # print(os.getpid(), "end")
    return results_dict


def _handle_mutation_search_task(task: MutationSearchTask) -> SearchResultsDict:
    generator = task.generator
    evaluator = task.evaluator
    mutator = task.mutator

    source_tunes_dict: Dict[str, Tune] = {}
    for gen_seed in task.generation_seed_strs:
        source_tunes_dict[gen_seed] = generator.generateTune(Seed(gen_seed))

    results_dict: SearchResultsDict = {}
    for i in range(task.start_idx, task.end_idx):
        generator_seed_str = task.generation_seed_strs[i % len(task.generation_seed_strs)]
        source_tune = source_tunes_dict[generator_seed_str]

        tune_copy_for_mutation = deepcopy(source_tune)
        mutation_seed_str = task.base_mutation_seed_str + str(i)
        mutator.mutateTune(tune_copy_for_mutation, mutation_seed_str)

        evaluation = evaluator.evaluate(tune_copy_for_mutation)
        evaluation.generator_seed_str = generator_seed_str
        evaluation.mutator_seed_str = mutation_seed_str

        results_dict[mutation_seed_str] = evaluation

    return results_dict


class TuneFinder(TuneFinderInterface):
    def findTune(self, num_iterations: int, seed_str: str) -> Tune:

        generator = TuneGenerator()
        evaluator = TuneEvaluator()
        mutator = TuneMutator()

        async_random_search_tasks = self._create_async_tasks(num_iterations, seed_str, generator, evaluator, 100)

        with Pool(self._get_pool_size()) as p:
            results = p.map(_handle_generation_search_task, async_random_search_tasks)

        results_dict = self._merge_async_results(results)
        self._normalize_scores(results_dict)
        best_tune_evaluations = self._get_best_evaluations(results_dict)
        best_tunes_generation_seeds: List[str] = [x.generator_seed_str for x in best_tune_evaluations]

        mutation_search_tasks = self._generate_mutation_search_tasks(num_iterations, best_tunes_generation_seeds)

        with Pool(self._get_pool_size()) as p:
            results = p.map(_handle_mutation_search_task, mutation_search_tasks)
        results_dict = self._merge_async_results(results)
        self._normalize_scores(results_dict)
        best_tune_evaluation = self._get_best_evaluations(results_dict, 1)[0]

        self._generate_tune_by_mutation_chain(best_tune_evaluation.generator_seed_str,
                                              [best_tune_evaluation.mutator_seed_str])

        return tunes[0]

    def _normalize_scores(self, results_dict: SearchResultsDict):
        min_harmony: Optional[float] = None
        max_harmony: Optional[float] = None

        min_rhythmicality: Optional[float] = None
        max_rhythmicality: Optional[float] = None

        min_content_score: Optional[float] = None
        max_content_score: Optional[float] = None

        for seed_str in results_dict:
            evaluation = results_dict[seed_str]

            min_rhythmicality = evaluation.rhythmicality_score if min_rhythmicality is None else min(
                min_rhythmicality,
                evaluation.rhythmicality_score)
            max_rhythmicality = evaluation.rhythmicality_score if max_rhythmicality is None else max(
                max_rhythmicality,
                evaluation.rhythmicality_score)

            min_harmony = evaluation.harmony_score if min_harmony is None else min(min_harmony,
                                                                                   evaluation.harmony_score)
            max_harmony = evaluation.harmony_score if max_harmony is None else max(max_harmony,
                                                                                   evaluation.harmony_score)

            min_content_score = evaluation.content_score if min_content_score is None else min(min_content_score,
                                                                                               evaluation.content_score)
            max_content_score = evaluation.content_score if max_content_score is None else max(max_content_score,
                                                                                               evaluation.content_score)

        for seed_str in results_dict:
            evaluation = results_dict[seed_str]
            evaluation.content_score = self._normalize_one_score(evaluation.content_score, min_content_score,
                                                                 max_content_score)
            evaluation.harmony_score = self._normalize_one_score(evaluation.harmony_score, min_harmony,
                                                                 max_harmony)
            evaluation.rhythmicality_score = self._normalize_one_score(evaluation.rhythmicality_score,
                                                                       min_rhythmicality, max_rhythmicality)

    def _normalize_one_score(self, raw_score: float, min_score: float, max_score: float) -> float:
        if min_score == max_score:
            return 0.0
        else:
            return (raw_score - min_score) / (max_score - min_score)

    def _get_best_evaluations(self, normalized_results_dict: SearchResultsDict,
                              how_many: int) -> List[TuneEvaluationResult]:
        evaluations = list(normalized_results_dict.values())

        def overall_score_calculator(x: TuneEvaluationResult) -> float:
            return x.rhythmicality_score + x.harmony_score * 5 + x.content_score

        evaluations.sort(key=overall_score_calculator, reverse=True)
        return evaluations[0:how_many]

    def _create_async_tasks(self, num_iterations: int, base_seed_str: str, generator: TuneGenerator,
                            evaluator: TuneEvaluator, chunk_size: int) -> List[GenerationSearchTask]:

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

    def _merge_async_results(self, results: List[SearchResultsDict]) -> SearchResultsDict:
        merged_result = {}

        for result in results:
            merged_result = {**merged_result, **result}

        return merged_result

    def _get_pool_size(self) -> int:
        return 4

    def _generate_mutation_search_tasks(self, num_iterations, best_tunes_generation_seeds) -> List:

        pass

    def _generate_tune_by_mutation_chain(self, generator: TuneGenerator, Mutation: TuneMutator, generator_seed_str: str,
                                         mutation_seed_str_chain: List[str]) -> Tune:
        pass
