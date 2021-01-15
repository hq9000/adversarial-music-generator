import logging
from copy import deepcopy
from dataclasses import dataclass
from multiprocessing.pool import Pool
from typing import Dict, List, Callable

from adversarial_music_generator.find_tunes_task import FindTunesTask
from adversarial_music_generator.interfaces import TuneGeneratorInterface, TuneMutatorInterface, \
    TuneEvaluatorInterface, EvaluationReducerInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.models.tune_blueprint import TuneBlueprint
from adversarial_music_generator.models.tune_evaluation_result import TuneEvaluationResult
from adversarial_music_generator.tune_finder_interface import TuneFinderInterface

SearchResultsDict = Dict[str, TuneEvaluationResult]
MutationSearchResultsDict = Dict[str, TuneEvaluationResult]
ProgressReportingFunction = Callable[[str, int, int], None]


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
    initial_tunes_blueprints: List[TuneBlueprint]
    base_mutation_seed_str: str
    start_idx: int
    end_idx: int
    generator: TuneGeneratorInterface
    evaluator: TuneEvaluatorInterface
    mutator: TuneMutatorInterface


def _generate_tune_by_blueprint(blueprint: TuneBlueprint, generator: TuneGeneratorInterface,
                                mutator: TuneMutatorInterface) -> Tune:
    tune = generator.generate_tunes([blueprint.generation_seed])[0]
    for mutation_seed in blueprint.mutation_seeds:
        mutator.mutate_tune(tune, mutation_seed)

    return tune


def _handle_generation_search_task(task: GenerationSearchTask) -> List[TuneEvaluationResult]:
    logging.info(f"generation {task.start_idx} - {task.end_idx}")

    generator = task.generator
    evaluator = task.evaluator

    seeds = [task.base_seed_str + str(i) for i in range(task.start_idx, task.end_idx)]

    tunes = generator.generate_tunes(seeds)
    evaluations = evaluator.evaluate_tunes(tunes)

    if len(tunes) != len(evaluations) or len(seeds) != len(evaluations):
        raise TuneFinderError('size mismatch (error: 93bf5bcc)')

    for seed, evaluation in zip(seeds, evaluations):
        evaluation.blueprint = TuneBlueprint(generation_seed=seed, mutation_seeds=[])

    return evaluations


def _handle_mutation_search_task(task: MutationSearchTask) -> List[TuneEvaluationResult]:
    evaluator = task.evaluator
    mutator = task.mutator

    source_tunes = [_generate_tune_by_blueprint(x, task.generator, task.mutator) for x in task.initial_tunes_blueprints]

    mutated_tunes: List[Tune] = []
    mutated_tunes_blueprints: List[TuneBlueprint] = []

    for i in range(task.start_idx, task.end_idx):
        source_tune = source_tunes[i % len(source_tunes)]
        source_tune_blueprint = task.initial_tunes_blueprints[i % len(source_tunes)]

        tune_copy_for_mutation = deepcopy(source_tune)
        cloned_blueprint = deepcopy(source_tune_blueprint)

        if i >= len(task.initial_tunes_blueprints):
            # first N tunes (one for every original seed)
            # go unmutated to leave the original
            # tunes in the evaluated set (in case no mutations bring any
            # improvement)
            mutation_seed = task.base_mutation_seed_str + str(i)
        else:
            mutation_seed = TuneMutatorInterface.SPECIAL_SEED_STR_TO_LEAVE_TUNE_UNMUTATED

        mutator.mutate_tune(tune_copy_for_mutation, mutation_seed)
        cloned_blueprint.mutation_seeds.append(mutation_seed)

        mutated_tunes.append(tune_copy_for_mutation)
        mutated_tunes_blueprints.append(cloned_blueprint)

    evaluations = evaluator.evaluate_tunes(mutated_tunes)

    for (evaluation, blueprint) in zip(evaluations, mutated_tunes_blueprints):
        evaluation.blueprint = blueprint

    return evaluations


class TuneFinder(TuneFinderInterface):
    def find_tunes(self, find_task: FindTunesTask) -> List[Tune]:

        chunk_size = 150

        random_search_tasks = self._generate_random_search_tasks(
            num_iterations=find_task.num_generation_iterations,
            base_seed_str=find_task.base_seed,
            generator=find_task.generator,
            evaluator=find_task.evaluator,
            chunk_size=chunk_size
        )

        def progress_reporting_function(phase: str, iterations_done: int, total_iterations: int):
            print(phase, iterations_done, "of", total_iterations)

        random_search_results = self._run_tasks(
            find_task=find_task,
            processing_function=_handle_generation_search_task,
            tasks=random_search_tasks,
            progress_reporting_function=progress_reporting_function,
            phase_name='random search')

        num_tunes_to_mutate = find_task.num_tunes_to_keep_from_generation
        best_tune_evaluations: List[TuneEvaluationResult] = self._get_best_evaluations(random_search_results,
                                                                                       find_task.reducer,
                                                                                       num_tunes_to_mutate)

        best_blueprints: List[TuneBlueprint] = [x.blueprint for x in best_tune_evaluations]

        for epoch in range(find_task.num_mutation_epochs):
            mutation_search_tasks = self._generate_mutation_search_tasks(
                num_iterations=find_task.num_mutation_iterations_in_epoch,
                best_tunes_blueprints=best_blueprints,
                evaluator=find_task.evaluator,
                mutator=find_task.mutator,
                generator=find_task.generator,
                chunk_size=chunk_size,
                base_mutation_seed_str=find_task.base_seed + "_mutation"
            )

            mutation_results = self._run_tasks(
                find_task=find_task,
                processing_function=_handle_mutation_search_task,
                tasks=mutation_search_tasks,
                progress_reporting_function=progress_reporting_function,
                phase_name="mutation"
            )

            if epoch < find_task.num_mutation_epochs - 1:
                num_tunes_to_keep = find_task.num_tunes_to_keep_after_mutation_epoch
            else:
                num_tunes_to_keep = find_task.num_tunes_to_find

            best_tune_evaluations = self._get_best_evaluations(mutation_results, find_task.reducer,
                                                               num_tunes_to_keep)

            best_blueprints = [x.blueprint for x in best_tune_evaluations]

        return [_generate_tune_by_blueprint(bp, find_task.generator, find_task.mutator) for bp in best_blueprints]

    def _run_tasks(self, find_task: FindTunesTask, processing_function: callable, tasks: List,
                   progress_reporting_function: ProgressReportingFunction, phase_name: str) -> List:

        results: List = []

        def register_result(result):
            results.append(result)
            progress_reporting_function(phase_name, len(results), len(tasks))

        if find_task.parallelize:
            with Pool(self._get_pool_size()) as p:
                for task in tasks:
                    p.apply_async(processing_function, (task,), callback=register_result)
                p.close()
                p.join()
        else:
            for task in tasks:
                result = processing_function(task)
                results.append(result)
                progress_reporting_function(phase_name, len(results), len(tasks))

        return self._merge_async_results(results)

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

    def _generate_mutation_search_tasks(self, num_iterations, best_tunes_blueprints: List[TuneBlueprint],
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
                initial_tunes_blueprints=best_tunes_blueprints,
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
