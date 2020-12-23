from adversarial_music_generator.interfaces import TuneMutatorInterface, TuneGeneratorInterface
from adversarial_music_generator.seed import Seed


class TuneMutator(TuneMutatorInterface):
    def mutateTune(self, generator: TuneGeneratorInterface, num_iterations: int, tune_seed: str):
        tune = generator.generateTune(Seed(tune_seed))
