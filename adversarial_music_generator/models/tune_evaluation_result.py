from dataclasses import dataclass
from typing import Dict


class TuneEvaluationError(Exception):
    pass


class TuneEvaluationResult:

    def __init__(self):
        self._aspects: Dict[str, float] = {}
        pass

    def set_aspect_value(self, aspect: str, value: float):
        self._aspects[aspect] = value

    def get_aspect_value(self, aspect: str) -> float:
        if aspect not in self._aspects:
            raise TuneEvaluationError(f"aspect named {aspect} has not been set in this evaluation (error: 7d722882)")
        return self._aspects[aspect]
