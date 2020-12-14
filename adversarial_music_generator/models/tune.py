from dataclasses import dataclass
from typing import List

from adversarial_music_generator.models.instrument import Instrument


@dataclass
class Note:
    note: int
    start_time: float
    end_time: float
    velocity: float


class Track:
    def __init__(self, instrument: Instrument):
        self.instrument = instrument
        self.notes: List[Note] = []


class Tune:
    def __init__(self):
        self.tracks: List[Track] = []
        pass
