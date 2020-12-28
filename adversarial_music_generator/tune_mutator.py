from adversarial_music_generator.interfaces import TuneMutatorInterface, TuneGeneratorInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.seed import Seed


class TuneMutator(TuneMutatorInterface):


    def mutate_tune(self, tune: Tune, seed_str: str):
        pass
