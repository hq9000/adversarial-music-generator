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

task = FindTunesTask(
    generator=generator,
    evaluator=evaluator,
    reducer=reducer,
    mutator=mutator,
    num_generation_iterations=20000,
    num_mutation_iterations=20000,
    num_tunes_to_mutate=4,
    base_seed="whatever",
    num_tunes_to_find=3
)

tunes = finder.find_tunes(task)

for i, tune in enumerate(tunes):
    to_midi_converter = TuneToMidiConverter()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    to_midi_converter.convert(tune, dir_path + '/output/' + str(i) + ".mid")
