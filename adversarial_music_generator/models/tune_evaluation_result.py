from dataclasses import dataclass


@dataclass
class TuneEvaluationResult:
    rhythmicality_score: float = 0.0
    harmony_score: float = 0.0
    content_score: float = 0.0
    seed_str: str = ''
