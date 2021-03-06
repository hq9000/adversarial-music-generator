from typing import List, Iterator

from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.track import Track


class Tune:
    def __init__(self):
        self.tracks: List[Track] = []
        self.bpm: float = 120.0
        self.start_time: float = 0.0
        self.end_time: float = 10.0

    def all_notes(self) -> Iterator[Note]:
        for track in self.tracks:
            for note in track.notes:
                yield note

    @property
    def num_notes(self) -> int:
        res = 0
        for track in self.tracks:
            res += len(track.notes)

        return res
