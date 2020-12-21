import os
import unittest

from adversarial_music_generator.seed import Seed
from adversarial_music_generator.tune_finder import TuneFinder
from adversarial_music_generator.tune_generator import TuneGenerator
from adversarial_music_generator.tune_to_midi_converter import TuneToMidiConverter


class TuneGeneratorTestCase(unittest.TestCase):
    def test_something(self):
        tune_finder = TuneFinder()
        seed = 'whatever1'
        num_iterations = 1000

        for seed in ['a']:
            tune = tune_finder.findTune(num_iterations, seed)
            dir_path = os.path.dirname(os.path.realpath(__file__))
            converter = TuneToMidiConverter()
            converter.convert(tune, dir_path + "/output/out_" + seed + "_" + str(num_iterations) + ".mid")


if __name__ == '__main__':
    unittest.main()
