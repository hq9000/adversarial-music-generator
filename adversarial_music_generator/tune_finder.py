from abc import ABC
from typing import Optional

from adversarial_music_generator.interfaces import TuneFinderInterface
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.seed import Seed
from adversarial_music_generator.tune_evaluator import TuneEvaluator
from adversarial_music_generator.tune_generator import TuneGenerator


class TuneFinder(TuneFinderInterface):
    def findTune(self, num_iterations: int, seed_str: str) -> Optional[Tune]:
        generator = TuneGenerator()
        evaluator = TuneEvaluator()

        max_score: float = 0
        best_tune: Optional[Tune] = None

        for i in range(num_iterations):
            seed = Seed(seed_str + str(i))
            tune = generator.generateTune(seed)
            evaluation = evaluator.evaluate(tune)
            score = evaluation.harmony + evaluation.rhythmicality
            if score > max_score:
                max_score = score
                best_tune = tune

        return best_tune
