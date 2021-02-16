from adversarial_music_generator.interfaces import TuneProcessorInterface
from adversarial_music_generator.models.tune import Tune


class DoNothingPostprocessor(TuneProcessorInterface):
    def process(self, tune: Tune, base_seed: str, tune_seed: str):
        pass
