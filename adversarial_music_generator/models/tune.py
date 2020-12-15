from typing import List

from adversarial_music_generator.models.track import Track


class Tune:
    def __init__(self):
        self.tracks: List[Track] = []
        self.bpm: float = 120.0
        self.grid_start: float = 0.0
