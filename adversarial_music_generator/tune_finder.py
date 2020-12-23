import os
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

RandomSearchResultsDict = Dict[str, TuneEvaluationResult]


@dataclass
class AsyncRandomSearchTask:
    base_seed_str: str
    start_idx: int
    end_idx: int
    generator: TuneGenerator
    evaluator: TuneEvaluator


def _perform_random_search(task: AsyncRandomSearchTask) -> RandomSearchResultsDict:
    # print(os.getpid(), "start")

    generator = task.generator
    evaluator = task.evaluator

    results_dict: RandomSearchResultsDict = {}
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

        evaluation.seed_str = sequence_seed_str
        results_dict[sequence_seed_str] = evaluation

    # print(os.getpid(), "end")
    return results_dict


class TuneFinder(TuneFinderInterface):
    def findTune(self, num_iterations: int, seed_str: str) -> Tune:

        generator = TuneGenerator()
        evaluator = TuneEvaluator()

        async_tasks = self._create_async_tasks(num_iterations, seed_str, generator, evaluator, 100)

        with Pool(self._get_pool_size()) as p:
            results = p.map(_perform_random_search, async_tasks)

        results_dict = self._merge_async_results(results)
        self._normalize_scores(results_dict)
        best_tune_evaluations = self._get_best_evaluations(results_dict, 1)

        tunes = [generator.generateTune(Seed(x.seed_str)) for x in best_tune_evaluations]
        return tunes[0]

    def _normalize_scores(self, results_dict: RandomSearchResultsDict):
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

    def _get_best_evaluations(self, normalized_results_dict: RandomSearchResultsDict,
                              how_many: int) -> List[TuneEvaluationResult]:
        evaluations = list(normalized_results_dict.values())

        def overall_score_calculator(x: TuneEvaluationResult) -> float:
            return x.rhythmicality_score + x.harmony_score * 5 + x.content_score

        evaluations.sort(key=overall_score_calculator, reverse=True)
        return evaluations[0:how_many]

    def _create_async_tasks(self, num_iterations: int, base_seed_str: str, generator: TuneGenerator,
                            evaluator: TuneEvaluator, chunk_size: int) -> List[AsyncRandomSearchTask]:

        cursor = 0
        tasks = []
        while cursor < num_iterations:
            task = AsyncRandomSearchTask(
                start_idx=cursor,
                end_idx=min(cursor + chunk_size, num_iterations),
                generator=generator,
                evaluator=evaluator,
                base_seed_str=base_seed_str
            )
            tasks.append(task)
            cursor += chunk_size

        return tasks

    def _merge_async_results(self, results: List[RandomSearchResultsDict]) -> RandomSearchResultsDict:
        merged_result = {}

        for result in results:
            merged_result = {**merged_result, **result}

        return merged_result

    def _get_pool_size(self) -> int:
        return 4
