from dataclasses import dataclass


@dataclass
class Note:
    note: int
    start_time: float
    end_time: float
    velocity: float
