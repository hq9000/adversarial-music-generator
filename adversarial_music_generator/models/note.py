from dataclasses import dataclass


@dataclass
class Note:
    note: int
    start_time_seconds: float
    end_time_seconds: float
    velocity: int
