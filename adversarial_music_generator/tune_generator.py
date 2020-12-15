from abc import ABC

from adversarial_music_generator.interfaces import TuneGeneratorInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.seed import Seed


class TuneGenerator(TuneGeneratorInterface):
    def generateTune(self, seed: Seed) -> Tune:
        res = Tune()
        return res
