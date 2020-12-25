from adversarial_music_generator.interfaces import TuneMutatorInterface, TuneGeneratorInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.seed import Seed


class TuneMutator(TuneMutatorInterface):
    SPECIAL_SEED_STR_TO_LEAVE_TUNE_UNMUTATED = 'transparent'

    def mutateTune(self, tune: Tune, seed_str: str):
        pass
