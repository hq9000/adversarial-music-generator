from adversarial_music_generator.interfaces import TuneProcessorInterface
from adversarial_music_generator.models.tune import Tune


class DoNothingPostprocessor(TuneProcessorInterface):
    def process(self, tune: Tune, processor_seed: str):
        pass

