from dataclasses import dataclass
from typing import List


@dataclass
class TuneBlueprint:
    generation_seed: str
    mutation_seeds: List[str]
