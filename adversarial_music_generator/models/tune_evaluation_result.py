from dataclasses import dataclass
from typing import Dict, List


class TuneEvaluationError(Exception):
    pass


class TuneEvaluationResult:
    """
    instances of this class represent two things at once:
    - tune evaluation (possible after certain normalization)
    - seeds needed to reproduce the tune (but not the tune itself), namely:
      - generator seed
      - a list of mutator seeds
    """
    UNDEFINED_SEED = 'undefined'

    def __init__(self):
        self._aspects: Dict[str, float] = {}
        self.generator_seed: str = self.UNDEFINED_SEED
        self.mutator_seeds: List[str] = []
        pass

    def set_aspect_value(self, aspect: str, value: float):
        self._aspects[aspect] = value

    def get_aspect_value(self, aspect: str) -> float:
        if aspect not in self._aspects:
            raise TuneEvaluationError(f"aspect named {aspect} has not been set in this evaluation (error: 7d722882)")
        return self._aspects[aspect]

    def __iter__(self):
        return iter(self._aspects)
