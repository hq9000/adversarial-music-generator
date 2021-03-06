from dataclasses import dataclass
from typing import List


@dataclass
class TuneBlueprint:
    base_seed: str
    tune_seed: str
    mutation_seeds: List[str]
