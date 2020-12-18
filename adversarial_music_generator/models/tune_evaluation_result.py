from dataclasses import dataclass


@dataclass
class TuneEvaluationResult:
    rhythmicality: float = 0.0
    harmony: float = 0.0
    content: float = 0.0
