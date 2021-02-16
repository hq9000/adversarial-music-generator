from typing import Dict, Optional

from adversarial_music_generator.models.tune_blueprint import TuneBlueprint


class TuneEvaluationError(Exception):
    pass


class TuneEvaluationResult:
    """
    instances of this class contain:
    - a tune evaluation
    - a tune blueprint, that is, a structure that keeps tune_seeds
      needed to reproduce a tune (but not the tune itself)
    """
    UNDEFINED_SEED = 'undefined'

    def __init__(self):
        self._aspects: Dict[str, float] = {}
        self.blueprint: Optional[TuneBlueprint] = None
        pass

    def set_aspect_value(self, aspect: str, value: float):
        self._aspects[aspect] = value

    def get_aspect_value(self, aspect: str) -> float:
        if aspect not in self._aspects:
            raise TuneEvaluationError(f"aspect named {aspect} has not been set in this evaluation (error: 7d722882)")
        return self._aspects[aspect]

    def __iter__(self):
        return iter(self._aspects)
