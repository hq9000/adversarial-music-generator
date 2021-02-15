import unittest

from adversarial_music_generator.demo.naive_random.donothing_postprocessor import DoNothingPostprocessor
from adversarial_music_generator.demo.naive_random.naive_random_evaluator import NaiveRandomEvaluator
from adversarial_music_generator.demo.naive_random.naive_random_generator import NaiveRandomGenerator
from adversarial_music_generator.demo.naive_random.naive_random_mutator import NaiveRandomMutator
from adversarial_music_generator.demo.naive_random.naive_random_reducer import NaiveRandomReducer
from adversarial_music_generator.find_tunes_task import FindTunesTask
from adversarial_music_generator.tune_finder import TuneFinder


class MyTestCase(unittest.TestCase):
    def test_naive_random(self):
        finder = TuneFinder()

        generator = NaiveRandomGenerator()
        evaluator = NaiveRandomEvaluator(generator, "qwerty")
        reducer = NaiveRandomReducer()
        mutator = NaiveRandomMutator()

        base_seed = "whatever2"

        task = FindTunesTask(
            generator=generator,
            evaluator=evaluator,
            reducer=reducer,
            mutator=mutator,
            postprocessor=DoNothingPostprocessor(),
            num_generation_iterations=20,
            num_mutation_iterations_in_epoch=40,
            num_mutation_epochs=3,
            num_tunes_to_keep_from_generation=4,
            num_tunes_to_keep_after_mutation_epoch=4,
            base_seed=base_seed,
            num_tunes_to_find=3,
            parallelize=True
        )

        tunes = finder.find_tunes(task)

        self.assertEqual(3, len(tunes))
