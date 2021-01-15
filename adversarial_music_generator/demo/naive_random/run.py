import os

from adversarial_music_generator.demo.naive_random.naive_random_evaluator import NaiveRandomEvaluator
from adversarial_music_generator.demo.naive_random.naive_random_mutator import NaiveRandomMutator
from adversarial_music_generator.demo.naive_random.naive_random_reducer import NaiveRandomReducer
from adversarial_music_generator.find_tunes_task import FindTunesTask
from adversarial_music_generator.tune_finder import TuneFinder
from adversarial_music_generator.demo.naive_random.naive_random_generator import NaiveRandomGenerator
from adversarial_music_generator.tune_to_midi_converter import TuneToMidiConverter

finder = TuneFinder()

generator = NaiveRandomGenerator()
evaluator = NaiveRandomEvaluator()
reducer = NaiveRandomReducer()
mutator = NaiveRandomMutator()

base_seed = "whatever2"

task = FindTunesTask(
    generator=generator,
    evaluator=evaluator,
    reducer=reducer,
    mutator=mutator,
    num_generation_iterations=8000,
    num_mutation_iterations_in_epoch=4000,
    num_mutation_epochs=20,
    num_tunes_to_keep_from_generation=40,
    num_tunes_to_keep_after_mutation_epoch=40,
    base_seed=base_seed,
    num_tunes_to_find=3,
    parallelize=True
)

tunes = finder.find_tunes(task)

for i, tune in enumerate(tunes):
    to_midi_converter = TuneToMidiConverter()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    to_midi_converter.convert(tune, dir_path + '/output/' + base_seed + "_" + str(i) + ".mid")
